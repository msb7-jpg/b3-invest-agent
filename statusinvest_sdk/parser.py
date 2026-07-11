import html
import json
import re

from bs4 import BeautifulSoup

from statusinvest_sdk.exceptions import PageLayoutChangedError
from statusinvest_sdk.logger import logger


class StatusInvestParser:
    """Classe responsável por realizar o parsing de páginas HTML do StatusInvest usando BeautifulSoup."""

    @staticmethod
    def _clean_float(value_str: str) -> float:
        """Limpa strings monetárias/percentuais e converte para float."""
        if not value_str:
            return 0.0
        cleaned = value_str.strip().replace("R$", "").replace("%", "").strip()
        if cleaned == "-" or cleaned == "":
            return 0.0
        if "," in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError as e:
            raise ValueError(f"Não foi possível converter '{value_str}' para float: {e}")

    def _find_card_value(self, soup: BeautifulSoup, ticker: str, card_title_keyword: str, is_item_card: bool = False) -> float:
        """Busca um container (div.info ou div.item) cujo título corresponda à palavra-chave e extrai seu valor."""
        classes_to_check = ["item", "info"] if is_item_card else ["info", "item"]
        
        for class_name in classes_to_check:
            for div in soup.find_all("div", class_=class_name):
                title_elem = (
                    div.find("h3") or 
                    div.find("span", class_="title") or 
                    div.find("h4") or
                    div.find("span", class_="sub-value")
                )
                if not title_elem:
                    continue
                
                title_text = title_elem.text.strip().lower()
                keyword_lower = card_title_keyword.lower()
                
                if keyword_lower in title_text or (keyword_lower == "d.y" and title_text == "d.y"):
                    value_elem = (
                        div.find("strong", class_="value") or 
                        div.find("span", class_="value") or 
                        div.find("strong") or
                        div.find(class_="value")
                    )
                    if value_elem:
                        try:
                            return self._clean_float(value_elem.text)
                        except Exception as e:
                            logger.error(f"Erro ao converter valor do card '{title_text}' no ativo {ticker}: {e}")
                            
        selector_str = f"div.info/item contendo título com a palavra-chave '{card_title_keyword}'"
        logger.critical(f"Falha de layout! Ativo: {ticker} | Campo procurado: {card_title_keyword} | Seletor esperado: {selector_str}")
        raise PageLayoutChangedError(card_title_keyword, ticker, selector_str)

    def parse_fii_html(self, html_content: str, ticker: str) -> dict:
        """Realiza o parse dos principais indicadores de um FII a partir do HTML da sua página."""
        soup = BeautifulSoup(html_content, "html.parser")
        ticker = ticker.upper()
        data = {"ticker": ticker}

        # 1. Preço Atual
        data["price"] = self._find_card_value(soup, ticker, "Valor atual")

        # 2. Dividend Yield (DY)
        data["dy"] = self._find_card_value(soup, ticker, "dividend yield")

        # 3. P/VP
        data["p_vp"] = self._find_card_value(soup, ticker, "p/vp")

        # 4. Valor Patrimonial por Cota
        data["valor_patrimonial_cota"] = self._find_card_value(soup, ticker, "val. patrimonial")

        # Extração opcional do nome do fundo
        name_elem = soup.find("h1")
        if name_elem:
            parts = name_elem.text.split(" - ")
            if len(parts) > 1:
                data["company_name"] = parts[1].strip()

        return data

    def parse_acao_html(self, html_content: str, ticker: str) -> dict:
        """Realiza o parse dos principais indicadores de uma Ação a partir do HTML da sua página."""
        soup = BeautifulSoup(html_content, "html.parser")
        ticker = ticker.upper()
        data = {"ticker": ticker}

        # 1. Preço Atual
        data["price"] = self._find_card_value(soup, ticker, "Valor atual")

        # 2. Dividend Yield (DY)
        try:
            data["dy"] = self._find_card_value(soup, ticker, "d.y", is_item_card=True)
        except PageLayoutChangedError:
            data["dy"] = self._find_card_value(soup, ticker, "dividend yield")

        # 3. P/VP
        data["p_vp"] = self._find_card_value(soup, ticker, "p/vp", is_item_card=True)

        # 4. P/L
        data["p_l"] = self._find_card_value(soup, ticker, "p/l", is_item_card=True)

        # Nome opcional da empresa
        name_elem = soup.find("h1")
        if name_elem:
            parts = name_elem.text.split(" - ")
            if len(parts) > 1:
                data["company_name"] = parts[1].strip()

        return data

    def parse_fii_reports(self, html_content: str, ticker: str) -> list:
        """Realiza o parse de relatórios e comunicados a partir da página HTML do FII."""
        soup = BeautifulSoup(html_content, "html.parser")
        ticker = ticker.upper()
        
        # Localiza o elemento com a lista de comunicados contendo data-page
        elem = soup.find(class_="list", attrs={"data-controller": "fii"})
        if not elem or not elem.has_attr("data-page"):
            # Tenta um seletor mais genérico
            elem = soup.find(attrs={"data-page": True})
            
        if not elem:
            raise PageLayoutChangedError("Tabela de Comunicados (data-page)", ticker, "div.list[data-controller='fii']")
            
        try:
            raw_json = html.unescape(elem.get("data-page"))
            raw_list = json.loads(raw_json)
            reports = []
            
            for item in raw_list:
                reports.append({
                    "ticker": ticker,
                    "date": item.get("dataEntrega") or item.get("dataReferencia") or "sem data",
                    "category": item.get("description", "Comunicado Oficial"),
                    "description": item.get("description", "Documento enviado à CVM/B3"),
                    "download_url": item.get("link", "")
                })
            return reports
        except Exception as e:
            logger.critical(f"Erro ao parsear JSON de comunicados de FII: {e}")
            raise PageLayoutChangedError("Parse JSON Tabela de Comunicados", ticker, "data-page JSON parsing")

    def parse_acao_reports(self, html_content: str, ticker: str) -> list:
        """Realiza o parse de relatórios, notícias e comunicados a partir da página HTML da Ação."""
        soup = BeautifulSoup(html_content, "html.parser")
        ticker = ticker.upper()
        reports = []
        
        # 1. Tenta extrair documentos oficiais da CVM/B3 (input name="results")
        inputs_results = soup.find_all("input", attrs={"name": "results"})
        for inp in inputs_results:
            try:
                val = html.unescape(inp.get("value", ""))
                data = json.loads(val)
                if isinstance(data, dict) and "reports" in data:
                    for item in data["reports"]:
                        reports.append({
                            "ticker": ticker,
                            "date": item.get("date", "sem data"),
                            "category": item.get("typeDesc", "Comunicado Oficial"),
                            "description": item.get("description", "Documento Oficial"),
                            "download_url": item.get("url", "")
                        })
            except:
                pass
                
        # 2. Extrai notícias e informativos (input id="news-text-hidden")
        inp_news = soup.find("input", id="news-text-hidden")
        if inp_news:
            try:
                raw_json = html.unescape(inp_news.get("value", ""))
                data_dict = json.loads(raw_json)
                content_list = data_dict.get("content", [])
                
                for item in content_list:
                    date_str = item.get("publishDate_F") or item.get("publishDate") or "sem data"
                    title = re.sub('<[^<]+?>', '', item.get("title", "Sem título"))
                    
                    reports.append({
                        "ticker": ticker,
                        "date": date_str,
                        "category": "Notícia / Informativo",
                        "description": title,
                        "download_url": item.get("contentUrl", "")
                    })
            except Exception as e:
                logger.warning(f"Aviso: Erro ao parsear notícias para {ticker}: {e}")
                
        if not reports:
            raise PageLayoutChangedError("Tabela de Documentos/Notícias", ticker, "input[name='results'] / input#news-text-hidden")
            
        return reports

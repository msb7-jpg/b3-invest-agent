import requests
import json
from typing import List, Optional, Union
from statusinvest_sdk.logger import logger
from statusinvest_sdk.exceptions import StatusInvestError, StatusInvestConnectionError, PageLayoutChangedError
from statusinvest_sdk.models import AcaoModel, FiiModel, ReportModel
from statusinvest_sdk.parser import StatusInvestParser
from statusinvest_sdk.notifier import Notifier

class StatusInvestClient:
    """Cliente principal do SDK do StatusInvest.
    
    Oferece acesso híbrido:
    - Coleta em lote via API Interna (rápido e estável).
    - Coleta individual via Scraping BeautifulSoup (detalhado, sujeito a quebra).
    """

    def __init__(self, notifier: Optional[Notifier] = None):
        self.notifier = notifier
        self.parser = StatusInvestParser()
        
        self.base_url = "https://statusinvest.com.br"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        })

    def _request_api(self, category_type: int) -> List[dict]:
        """Faz a requisição para a API de busca avançada do StatusInvest e retorna a lista de dicionários crua."""
        url = f"{self.base_url}/category/advancedsearchresult"
        params = {
            "search": json.dumps({"CategoryType": category_type}),
            "CategoryType": category_type
        }
        
        try:
            logger.info(f"Consumindo API interna do StatusInvest para CategoryType={category_type}...")
            response = self.session.post(url, data=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if not isinstance(data, list):
                logger.warning("Resposta da API interna não retornou uma lista conforme esperado.")
                return []
            
            return data
        except requests.RequestException as e:
            msg = f"Erro de conexão com a API interna do StatusInvest: {e}"
            logger.error(msg)
            raise StatusInvestConnectionError(msg)
        except json.JSONDecodeError as e:
            msg = f"Erro ao decodificar JSON da API interna do StatusInvest: {e}"
            logger.error(msg)
            raise StatusInvestError(msg)

    def get_acoes_indicadores(self) -> List[AcaoModel]:
        """Obtém a lista de ações com seus múltiplos a partir da API interna."""
        raw_data = self._request_api(category_type=1)
        models = []
        for item in raw_data:
            try:
                models.append(AcaoModel(
                    ticker=item.get("ticker", ""),
                    price=item.get("price", 0.0),
                    dy=item.get("dy", None),
                    p_vp=item.get("p_vp", None),
                    p_l=item.get("p_l", None),
                    company_name=item.get("companyname", None)
                ))
            except Exception as e:
                logger.warning(f"Ignorando registro de ação inválido: {item.get('ticker')} | Erro: {e}")
        return models

    def get_fiis_indicadores(self) -> List[FiiModel]:
        """Obtém a lista de FIIs com seus múltiplos a partir da API interna."""
        raw_data = self._request_api(category_type=2)
        models = []
        for item in raw_data:
            try:
                models.append(FiiModel(
                    ticker=item.get("ticker", ""),
                    price=item.get("price", 0.0),
                    dy=item.get("dy", None),
                    p_vp=item.get("p_vp", None),
                    valor_patrimonial_cota=item.get("valorpatrimonialcota", None),
                    company_name=item.get("companyname", None),
                    sector_name=item.get("sectorname", None),
                    segment_name=item.get("segmentname", None)
                ))
            except Exception as e:
                logger.warning(f"Ignorando registro de FII inválido: {item.get('ticker')} | Erro: {e}")
        return models

    def get_fii(self, ticker: str, force_scraping: bool = False) -> FiiModel:
        """Busca dados de um FII específico (estratégia híbrida)."""
        ticker = ticker.upper()
        
        if not force_scraping:
            try:
                fiis = self.get_fiis_indicadores()
                for fii in fiis:
                    if fii.ticker == ticker:
                        logger.info(f"FII {ticker} encontrado via API Interna.")
                        return fii
            except Exception as e:
                logger.warning(f"Falha ao buscar FII via API interna, recorrendo a scraping HTML: {e}")
        
        logger.info(f"Iniciando scraping HTML para FII: {ticker}...")
        url = f"{self.base_url}/fundos-imobiliarios/{ticker.lower()}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            parsed_data = self.parser.parse_fii_html(response.text, ticker)
            return FiiModel(**parsed_data)
        except PageLayoutChangedError as e:
            if self.notifier:
                self.notifier.send_alert(ticker=ticker, field_name=e.field_name, selector=e.selector)
            raise e
        except requests.RequestException as e:
            msg = f"Erro de rede ao carregar página de FII {ticker}: {e}"
            logger.error(msg)
            raise StatusInvestConnectionError(msg)

    def get_acao(self, ticker: str, force_scraping: bool = False) -> AcaoModel:
        """Busca dados de uma Ação específica (estratégia híbrida)."""
        ticker = ticker.upper()
        
        if not force_scraping:
            try:
                acoes = self.get_acoes_indicadores()
                for acao in acoes:
                    if acao.ticker == ticker:
                        logger.info(f"Ação {ticker} encontrado via API Interna.")
                        return acao
            except Exception as e:
                logger.warning(f"Falha ao buscar Ação via API interna, recorrendo a scraping HTML: {e}")

        logger.info(f"Iniciando scraping HTML para Ação: {ticker}...")
        url = f"{self.base_url}/acoes/{ticker.lower()}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            parsed_data = self.parser.parse_acao_html(response.text, ticker)
            return AcaoModel(**parsed_data)
        except PageLayoutChangedError as e:
            if self.notifier:
                self.notifier.send_alert(ticker=ticker, field_name=e.field_name, selector=e.selector)
            raise e
        except requests.RequestException as e:
            msg = f"Erro de rede ao carregar página de Ação {ticker}: {e}"
            logger.error(msg)
            raise StatusInvestConnectionError(msg)
            
    def get_reports(self, ticker: str) -> List[ReportModel]:
        """Extrai relatórios e comunicados de um ativo (Ação ou FII)."""
        ticker = ticker.upper()
        
        logger.info(f"Coletando relatórios de: {ticker}...")
        url = f"{self.base_url}/acoes/{ticker.lower()}"
        is_fii = False
            
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 404:
                is_fii = True
                url = f"{self.base_url}/fundos-imobiliarios/{ticker.lower()}"
                response = self.session.get(url, timeout=15)
            
            response.raise_for_status()
            
            if is_fii:
                raw_reports = self.parser.parse_fii_reports(response.text, ticker)
            else:
                raw_reports = self.parser.parse_acao_reports(response.text, ticker)
                
            models = []
            for item in raw_reports:
                try:
                    models.append(ReportModel(**item))
                except Exception as e:
                    logger.warning(f"Ignorando comunicado inválido para {ticker}: {item} | Erro: {e}")
            return models
            
        except PageLayoutChangedError as e:
            if self.notifier:
                self.notifier.send_alert(ticker=ticker, field_name=e.field_name, selector=e.selector)
            raise e
        except requests.RequestException as e:
            msg = f"Erro de rede ao carregar relatórios do ativo {ticker}: {e}"
            logger.error(msg)
            raise StatusInvestConnectionError(msg)

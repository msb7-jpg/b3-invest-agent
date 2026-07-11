import requests
import json
import html
import hashlib
from typing import List, Dict
from bs4 import BeautifulSoup
from statusinvest_sdk.logger import logger
from statusinvest_sdk.exceptions import PageLayoutChangedError

class InsiderScraper:
    """Extrai dados de movimentações acionárias e posições de controle (Insider Trading)."""
    
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.base_url = "https://statusinvest.com.br"

    def get_posicao_acionaria(self, ticker: str) -> List[Dict]:
        """
        Extrai a tabela de Posição Acionária da ação ou FII.
        Essa tabela revela as movimentações (compra/venda) dos maiores acionistas e controladores.
        """
        ticker = ticker.upper()
        url = f"{self.base_url}/acoes/{ticker.lower()}"
        
        try:
            res = self.session.get(url, timeout=15)
            if res.status_code == 404:
                url = f"{self.base_url}/fundos-imobiliarios/{ticker.lower()}"
                res = self.session.get(url, timeout=15)
                
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, 'html.parser')
            inputs = soup.find_all("input", attrs={"name": "results"})
            
            for inp in inputs:
                try:
                    val = html.unescape(inp.get("value", ""))
                    data = json.loads(val)
                    if isinstance(data, list) and len(data) > 0 and "Acionista" in data[0]:
                        # Encontrou o JSON da posição acionária
                        posicoes = []
                        for pos in data:
                            # Ignora se não for dicionário
                            if not isinstance(pos, dict):
                                continue
                            
                            acionista = pos.get("Acionista", "Desconhecido")
                            data_alt = pos.get("DataUltimaAlteracao", "Sem Data")
                            perc = pos.get("PercentualTotal", "0")
                            qtd = pos.get("QuantidadeTotal", "0")
                            controlador = pos.get("AcionistaControlador", "não")
                            
                            # Gera um hash único baseado no acionista, data e percentual atual
                            raw_str = f"{ticker}-{acionista}-{data_alt}-{perc}-{qtd}".encode("utf-8")
                            md5_hash = hashlib.md5(raw_str).hexdigest()
                            
                            posicoes.append({
                                "hash": md5_hash,
                                "ticker": ticker,
                                "acionista": acionista,
                                "data_alteracao": data_alt,
                                "percentual": perc,
                                "quantidade": qtd,
                                "controlador": controlador
                            })
                        return posicoes
                except Exception:
                    pass
                    
            # Se chegou aqui, não encontrou a tabela no formato esperado
            logger.warning(f"Não foi possível encontrar a Posição Acionária para {ticker}.")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar posição acionária de {ticker}: {e}")
            return []

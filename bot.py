import hashlib
import os
import sys
from time import sleep

# Adiciona o diretório atual ao path para importar o sdk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from statusinvest_sdk.ai_analyzer import AIAnalyzer
from statusinvest_sdk.client import StatusInvestClient
from statusinvest_sdk.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from statusinvest_sdk.insider import InsiderScraper
from statusinvest_sdk.logger import logger
from statusinvest_sdk.notifier import TelegramNotifier
from statusinvest_sdk.storage import StateManager


def main():
    logger.info("Iniciando o Orquestrador StatusInvest AI Bot...")
    
    # Injeção de Dependência
    notifier = TelegramNotifier(token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID)
    
    client = StatusInvestClient(notifier=notifier)
    insider_scraper = InsiderScraper(session=client.session)
    state_manager = StateManager()
    ai = AIAnalyzer()

    
    # Carrega estado (Hashes MD5 já analisados)
    state = state_manager.load()
    has_new_data = False
    
    # Lista de ativos a monitorar
    from statusinvest_sdk.config import ATIVOS_MONITORADOS
    ativos = [ativo.strip() for ativo in ATIVOS_MONITORADOS if ativo.strip()]
    
    for ticker in ativos:
        logger.info(f"--- Processando ativo: {ticker} ---")
        
        # 1. Busca e analisa Relatórios / Fatos Relevantes
        try:
            reports = client.get_reports(ticker)
            for rep in reports:
                if "Notícia" in rep.category or "Informativo" in rep.category:
                    logger.info(f"Ignorando Notícia/Informativo para {ticker}: {rep.description}")
                    continue

                # Cria MD5 baseado no título e data
                raw_str = f"{ticker}-report-{rep.date}-{rep.description}"
                rep_hash = hashlib.md5(raw_str.encode("utf-8")).hexdigest()
                
                if rep_hash not in state.processed_hashes:
                    logger.info(f"Novo relatório detectado para {ticker}: {rep.description}")
                    
                    conteudo = f"O documento é um '{rep.category}' com o título/assunto: {rep.description}. Link: {rep.download_url}"
                    
                    # Extração Inteligente: Tenta ler como PDF, se falhar, tenta ler como HTML (ex: Formulários FNET)
                    try:
                        import io

                        import pypdf
                        import requests
                        from bs4 import BeautifulSoup
                        resp = requests.get(rep.download_url, timeout=15)
                        
                        if resp.status_code == 200:
                            is_pdf = False
                            try:
                                pdf_reader = pypdf.PdfReader(io.BytesIO(resp.content))
                                pdf_text = ""
                                for page in pdf_reader.pages:
                                    pdf_text += page.extract_text() + "\n"
                                
                                if pdf_text.strip():
                                    conteudo += f"\n\nTEXTO EXTRAÍDO DO DOCUMENTO (PDF):\n{pdf_text}"
                                    logger.info(f"Texto extraído como PDF com sucesso: {rep.download_url}")
                                    is_pdf = True
                            except Exception:
                                pass # Falhou em ler como PDF, não é um PDF válido
                                
                            # Fallback para HTML
                            if not is_pdf:
                                soup = BeautifulSoup(resp.text, 'html.parser')
                                html_text = soup.get_text(separator='\n', strip=True)
                                if html_text:
                                    conteudo += f"\n\nTEXTO EXTRAÍDO DO DOCUMENTO (HTML/FORM):\n{html_text}"
                                    logger.info(f"Texto extraído como HTML com sucesso: {rep.download_url}")
                    except Exception as e:
                        logger.warning(f"Não foi possível extrair conteúdo de {rep.download_url}: {e}")

                    # Usa o LLM para resumir e classificar
                    analise = ai.analyze_document(
                        ticker=ticker,
                        categoria=rep.category,
                        conteudo=conteudo
                    )
                    
                    # Notifica no Telegram
                    notifier.send_ai_analysis(
                        ticker=ticker,
                        categoria=rep.category,
                        titulo=rep.description,
                        sentimento=analise.sentimento,
                        explicacao=analise.explicacao,
                        url_doc=rep.download_url
                    )
                    
                    # Adiciona ao estado
                    state.processed_hashes.add(rep_hash)
                    has_new_data = True
        except Exception as e:
            logger.error(f"Erro ao processar relatórios de {ticker}: {e}")
            
        # 2. Busca e analisa Movimentações Acionárias (Insider Trading)
        try:
            posicoes = insider_scraper.get_posicao_acionaria(ticker)
            for pos in posicoes:
                h = pos["hash"]
                if h not in state.processed_hashes:
                    logger.info(f"Nova movimentação acionária detectada para {ticker}: {pos['acionista']}")
                    
                    texto_mov = (
                        f"Acionista: {pos['acionista']} (Controlador: {pos['controlador']})\n"
                        f"Percentual Atual: {pos['percentual']}%\n"
                        f"Quantidade Total: {pos['quantidade']} ações\n"
                        f"Data de Atualização CVM: {pos['data_alteracao']}"
                    )
                    
                    analise = ai.analyze_document(
                        ticker=ticker,
                        categoria="Movimentação Acionária / Insider Trading",
                        conteudo=texto_mov
                    )
                    
                    notifier.send_ai_analysis(
                        ticker=ticker,
                        categoria="Posição Acionária",
                        titulo=f"Atualização: {pos['acionista']}",
                        sentimento=analise.sentimento,
                        explicacao=analise.explicacao
                    )
                    
                    state.processed_hashes.add(h)
                    has_new_data = True
        except Exception as e:
            logger.error(f"Erro ao processar posição acionária de {ticker}: {e}")
            
        # Pausa leve para não sobrecarregar as APIs
        sleep(2)
        
    if has_new_data:
        state_manager.save(state)
        logger.info("Estado atualizado e salvo com sucesso.")
    else:
        logger.info("Nenhuma novidade encontrada. Estado mantido.")

if __name__ == "__main__":
    main()

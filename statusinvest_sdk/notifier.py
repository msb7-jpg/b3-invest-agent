import requests
import os
import datetime
from abc import ABC, abstractmethod
from statusinvest_sdk.logger import logger
from statusinvest_sdk.config import LOGS_DIR

class Notifier(ABC):
    """Classe base para os notificadores do sistema."""
    
    @abstractmethod
    def send_alert(self, ticker: str, field_name: str, selector: str) -> bool:
        pass
        
    @abstractmethod
    def send_ai_analysis(self, ticker: str, categoria: str, titulo: str, sentimento: str, explicacao: str, url_doc: str = "") -> bool:
        pass


class TelegramNotifier(Notifier):
    """Classe responsável pelo envio de alertas e análises para o Telegram do desenvolvedor."""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage" if self.token else ""

    def send_alert(self, ticker: str, field_name: str, selector: str) -> bool:
        if not self.token or not self.chat_id:
            logger.debug(f"Envio de alerta ignorado (Telegram não configurado) para {ticker.upper()}.")
            return False

        text = (
            f"⚠️ <b>[SDK CRITICAL] Mudança de Layout</b>\n\n"
            f"<b>Ativo:</b> {ticker.upper()}\n"
            f"<b>Campo Falhou:</b> <code>{field_name}</code>\n"
            f"<b>Seletor Tentado:</b> <code>{selector}</code>\n\n"
            f"🚨 <i>Ação necessária: Atualize os seletores do BeautifulSoup!</i>"
        )
        
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Falha ao enviar alerta para o Telegram: {e}")
            return False

    def send_ai_analysis(self, ticker: str, categoria: str, titulo: str, sentimento: str, explicacao: str, url_doc: str = "") -> bool:
        if not self.token or not self.chat_id:
            logger.debug(f"Notificação IA ignorada (Telegram não configurado). Ativo: {ticker} | {titulo}")
            return False
            
        emoji = "🟢" if sentimento == "Positivo" else "🔴" if sentimento == "Negativo" else "⚪"
        
        text = (
            f"🤖 <b>[StatusInvest AI Analysis]</b>\n\n"
            f"<b>Ativo:</b> {ticker.upper()}\n"
            f"<b>Categoria:</b> {categoria}\n"
            f"<b>Evento:</b> {titulo}\n"
            f"<b>Sentimento:</b> {emoji} {sentimento}\n\n"
            f"<b>Explicação Detalhada:</b>\n{explicacao}\n"
        )
        if url_doc:
            text += f"\n🔗 <a href='{url_doc}'>Acessar Documento</a>"
            
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Falha ao enviar Análise de IA para o Telegram: {e}")
            return False


class FileNotifier(Notifier):
    """Notificador de debug que escreve mensagens em um arquivo local."""
    
    def __init__(self, filename: str = "notifications_debug.txt"):
        self.filepath = os.path.join(LOGS_DIR, filename)
        
    def _write(self, text: str):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(f"\n--- [{timestamp}] NOVA NOTIFICAÇÃO ---\n")
                f.write(text)
                f.write("\n---------------------------------------\n")
            logger.info(f"Notificação escrita em arquivo: {self.filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao escrever notificação no arquivo: {e}")
            return False

    def send_alert(self, ticker: str, field_name: str, selector: str) -> bool:
        text = f"[LAYOUT CHANGE ALERT] Ativo: {ticker.upper()} | Campo: {field_name} | Seletor: {selector}"
        return self._write(text)

    def send_ai_analysis(self, ticker: str, categoria: str, titulo: str, sentimento: str, explicacao: str, url_doc: str = "") -> bool:
        text = (
            f"[AI ANALYSIS] Ativo: {ticker.upper()}\n"
            f"Categoria: {categoria}\n"
            f"Evento: {titulo}\n"
            f"Sentimento: {sentimento}\n"
            f"Explicação: {explicacao}\n"
        )
        if url_doc:
            text += f"Documento: {url_doc}\n"
        return self._write(text)

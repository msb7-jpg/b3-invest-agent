import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o arquivo .env do diretório raiz do projeto
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Ativos monitorados separados por vírgula
ATIVOS_MONITORADOS = os.environ.get("ATIVOS_MONITORADOS", "PETR4,TAEE11,XPML11").split(",")

# Caminho para logs
LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
SDK_LOG_FILE = LOGS_DIR / 'sdk_errors.log'

# Configurações da IA
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "http://desktop-wsl:8080")
OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "")

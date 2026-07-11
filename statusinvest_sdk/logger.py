import logging
import os
from sys import stdout

def setup_logger():
    """Configura o logger do SDK para console e arquivo local."""
    logger = logging.getLogger("StatusInvestSDK")
    logger.setLevel(logging.DEBUG)
    
    # Evita adicionar múltiplos handlers caso já existam
    if not logger.handlers:
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s')
        
        # Handler para o console (stdout)
        console_handler = logging.StreamHandler(stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)
        
        # Handler para arquivo local
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/sdk_errors.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.WARNING)  # Apenas WARNING e CRITICAL vão para o arquivo
        logger.addHandler(file_handler)
        
    return logger

logger = setup_logger()

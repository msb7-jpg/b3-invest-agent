import zlib
import os
from pathlib import Path
from statusinvest_sdk.models.state import ProcessedState
from statusinvest_sdk.logger import logger

class StateManager:
    """Gerencia o estado dos itens processados, serializando para JSON e comprimindo em formato binário (zlib)."""
    
    def __init__(self, filepath: str = None):
        if filepath is None:
            # Salva na raiz do workspace por padrão, ou em um diretório /data
            base_dir = Path(__file__).parent.parent
            self.filepath = os.path.join(base_dir, "data", "state.zlib")
        else:
            self.filepath = filepath
            
        # Garante que a pasta existe
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def load(self) -> ProcessedState:
        """Lê o arquivo binário, descomprime e carrega para o modelo Pydantic."""
        if not os.path.exists(self.filepath):
            logger.info("Arquivo de estado não encontrado. Criando um novo estado vazio.")
            return ProcessedState()
        
        try:
            with open(self.filepath, "rb") as f:
                compressed_data = f.read()
            
            json_data = zlib.decompress(compressed_data).decode("utf-8")
            state = ProcessedState.model_validate_json(json_data)
            logger.debug(f"Estado carregado com sucesso. {len(state.processed_hashes)} hashes mapeados.")
            return state
        except Exception as e:
            logger.error(f"Erro ao carregar o estado binário (ZLIB/JSON): {e}. Iniciando com estado vazio.")
            return ProcessedState()

    def save(self, state: ProcessedState) -> bool:
        """Serializa o modelo Pydantic para JSON, comprime com zlib e salva no arquivo binário."""
        try:
            json_data = state.model_dump_json().encode("utf-8")
            compressed_data = zlib.compress(json_data)
            
            with open(self.filepath, "wb") as f:
                f.write(compressed_data)
            logger.info(f"Estado salvo. Total de hashes: {len(state.processed_hashes)}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar o estado binário: {e}")
            return False

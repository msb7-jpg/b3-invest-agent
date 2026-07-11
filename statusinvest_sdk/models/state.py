from pydantic import BaseModel, Field
from typing import Set

class ProcessedState(BaseModel):
    """Modelo Pydantic que guarda o estado dos itens já processados pela IA."""
    processed_hashes: Set[str] = Field(default_factory=set)

from typing import Optional
from pydantic import BaseModel, Field, field_validator

class BaseTickerModel(BaseModel):
    ticker: str
    price: float
    dy: Optional[float] = Field(None, description="Dividend Yield em percentual (ex: 9.18)")
    p_vp: Optional[float] = Field(None, description="Preço / Valor Patrimonial")

    @field_validator("ticker", mode="before")
    @classmethod
    def clean_ticker(cls, v):
        if isinstance(v, str):
            return v.strip().upper()
        return v


class AcaoModel(BaseTickerModel):
    p_l: Optional[float] = Field(None, description="Preço / Lucro")
    company_name: Optional[str] = Field(None, description="Nome da empresa")


class FiiModel(BaseTickerModel):
    valor_patrimonial_cota: Optional[float] = Field(None, description="Valor Patrimonial por Cota")
    company_name: Optional[str] = Field(None, description="Nome do Fundo")
    sector_name: Optional[str] = Field(None, description="Setor do FII (Tijolo, Papel, etc.)")
    segment_name: Optional[str] = Field(None, description="Segmento do FII")

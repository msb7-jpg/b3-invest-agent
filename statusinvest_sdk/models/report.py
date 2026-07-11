from pydantic import BaseModel, Field

class ReportModel(BaseModel):
    ticker: str = Field(..., description="Ticker do ativo correspondente")
    date: str = Field(..., description="Data de publicação (dd/mm/aaaa)")
    category: str = Field(..., description="Categoria do documento (ex: Fato Relevante, Relatório Gerencial)")
    description: str = Field(..., description="Título ou descrição resumida do documento")
    download_url: str = Field(..., description="URL direta para download do documento em PDF/HTML")

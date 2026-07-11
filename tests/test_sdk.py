import pytest
from statusinvest_sdk import StatusInvestClient, AcaoModel, FiiModel, ReportModel
from statusinvest_sdk.exceptions import PageLayoutChangedError

@pytest.fixture
def client():
    return StatusInvestClient()

def test_get_acoes_indicadores(client):
    """Testa a coleta em lote de ações via API Interna."""
    acoes = client.get_acoes_indicadores()
    assert isinstance(acoes, list)
    assert len(acoes) > 0
    
    primeira = acoes[0]
    assert isinstance(primeira, AcaoModel)
    assert primeira.ticker != ""
    assert primeira.price > 0.0
    if primeira.p_l is not None:
        assert isinstance(primeira.p_l, float)
    if primeira.p_vp is not None:
        assert isinstance(primeira.p_vp, float)
    if primeira.dy is not None:
        assert isinstance(primeira.dy, float)

def test_get_fiis_indicadores(client):
    """Testa a coleta em lote de FIIs via API Interna."""
    fiis = client.get_fiis_indicadores()
    assert isinstance(fiis, list)
    assert len(fiis) > 0
    
    primeiro = fiis[0]
    assert isinstance(primeiro, FiiModel)
    assert primeiro.ticker != ""
    assert primeiro.price > 0.0
    if primeiro.p_vp is not None:
        assert isinstance(primeiro.p_vp, float)
    if primeiro.dy is not None:
        assert isinstance(primeiro.dy, float)
    if primeiro.valor_patrimonial_cota is not None:
        assert isinstance(primeiro.valor_patrimonial_cota, float)

def test_get_fii_individual_api(client):
    """Testa a busca de um FII específico via API Interna."""
    fii = client.get_fii("MXRF11", force_scraping=False)
    assert isinstance(fii, FiiModel)
    assert fii.ticker == "MXRF11"
    assert fii.price > 0.0
    assert fii.dy is not None
    assert fii.p_vp is not None

def test_get_fii_individual_scraping(client):
    """Testa a busca de um FII específico via Scraping BeautifulSoup."""
    fii = client.get_fii("MXRF11", force_scraping=True)
    assert isinstance(fii, FiiModel)
    assert fii.ticker == "MXRF11"
    assert fii.price > 0.0
    assert fii.dy is not None
    assert fii.p_vp is not None
    assert fii.valor_patrimonial_cota is not None
    if fii.company_name:
        assert "MAXI RENDA" in fii.company_name.upper()

def test_get_acao_individual_api(client):
    """Testa a busca de uma Ação específica via API Interna."""
    acao = client.get_acao("PETR4", force_scraping=False)
    assert isinstance(acao, AcaoModel)
    assert acao.ticker == "PETR4"
    assert acao.price > 0.0
    assert acao.dy is not None
    assert acao.p_vp is not None

def test_get_acao_individual_scraping(client):
    """Testa a busca de uma Ação específica via Scraping BeautifulSoup."""
    acao = client.get_acao("PETR4", force_scraping=True)
    assert isinstance(acao, AcaoModel)
    assert acao.ticker == "PETR4"
    assert acao.price > 0.0
    assert acao.dy is not None
    assert acao.p_vp is not None
    assert acao.p_l is not None

def test_get_reports_fii(client):
    """Testa a coleta de relatórios de um FII."""
    reports = client.get_reports("MXRF11")
    assert isinstance(reports, list)
    assert len(reports) > 0
    
    primeiro = reports[0]
    assert isinstance(primeiro, ReportModel)
    assert primeiro.ticker == "MXRF11"
    assert primeiro.date != ""
    assert primeiro.category != ""
    assert primeiro.description != ""
    assert primeiro.download_url != ""
    assert primeiro.download_url.startswith("http")

def test_get_reports_acao(client):
    """Testa a coleta de relatórios de uma Ação."""
    reports = client.get_reports("PETR4")
    assert isinstance(reports, list)
    assert len(reports) > 0
    
    primeiro = reports[0]
    assert isinstance(primeiro, ReportModel)
    assert primeiro.ticker == "PETR4"
    assert primeiro.date != ""
    assert primeiro.category != ""
    assert primeiro.description != ""
    assert primeiro.download_url != ""
    assert primeiro.download_url.startswith("http")

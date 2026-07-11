class StatusInvestError(Exception):
    """Exceção base para o SDK do StatusInvest."""
    pass


class StatusInvestConnectionError(StatusInvestError):
    """Exceção disparada quando ocorrem erros de conexão de rede, timeouts ou HTTP errors."""
    pass


class PageLayoutChangedError(StatusInvestError):
    """Exceção disparada quando uma mudança de layout é detectada na página do StatusInvest.
    
    Reporta o ativo, o campo e o seletor HTML que falhou para facilitar a depuração.
    """
    def __init__(self, field_name: str, ticker: str, selector: str):
        self.field_name = field_name
        self.ticker = ticker.upper()
        self.selector = selector
        self.message = (
            f"Mudança de Layout detectada em {self.ticker} -> "
            f"Falha ao extrair campo '{self.field_name}' usando o seletor: {self.selector}"
        )
        super().__init__(self.message)

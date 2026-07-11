# 📊 Gerenciador de Investimentos - B3

Aplicativo web para análise e rebalanceamento de carteira de investimentos baseado em planilhas exportadas da B3 (Brasil, Bolsa, Balcão).

## 🎯 Funcionalidades

- **📁 Importação de Planilha B3**: Arraste e solte ou selecione sua planilha de posição da B3 (formato `.xlsx`)
- **📊 Visualização da Carteira**: Resumo completo com valor total, classes de ativos e distribuição
- **🎯 Alocação Alvo**: Defina percentuais desejados para cada classe de ativo
- **📈 Recomendações de Rebalanceamento**: Calcula automaticamente quanto comprar ou vender para atingir a alocação alvo
- **💾 Persistência Local**: Seus dados são salvos no navegador e persistem entre sessões
- **🔄 Atualização Automática**: Suporte futuro para integração com Yahoo Finance para cotações em tempo real

## 🚀 Como Usar

### 1. Abrir o Aplicativo

Abra o arquivo `index.html` em seu navegador:

```bash
# Opção 1: Abrir diretamente
open index.html  # macOS
xdg-open index.html  # Linux
start index.html  # Windows

# Opção 2: Usar um servidor local (recomendado)
python3 -m http.server 8000
# Acesse: http://localhost:8000
```

### 2. Carregar Planilha da B3

1. **Exporte sua posição** da área logada da B3
2. **Arraste o arquivo** para a área de upload ou clique para selecionar
3. O aplicativo processará automaticamente todas as abas da planilha

### 3. Definir Alocação Desejada

1. Na seção "**🎯 Alocação Desejada**", defina o percentual que você deseja para cada classe
2. O total deve somar **100%** (o sistema indica em verde quando correto)
3. Clique em "**Salvar Alocação**" para persistir suas preferências

### 4. Analisar Recomendações

O aplicativo mostrará:
- ✅ Classes que precisam de **COMPRA** (abaixo da meta)
- ❌ Classes que precisam de **VENDA** (acima da meta)
- Valores exatos em R$ para rebalancear

## 📁 Estrutura do Projeto

```
investidor/
├── index.html              # Interface principal
├── app.js                  # Lógica da aplicação
├── README.md              # Este arquivo
└── posicao-*.xlsx         # Sua planilha da B3 (não versionada)
```

## 🔧 Tecnologias Utilizadas

- **HTML5**: Estrutura semântica
- **Tailwind CSS**: Estilização responsiva via CDN
- **JavaScript (Vanilla)**: Lógica sem frameworks
- **SheetJS (xlsx)**: Parser de arquivos Excel
- **localStorage**: Persistência de dados no navegador

## 📊 Classes de Ativos Suportadas

O aplicativo identifica automaticamente as seguintes classes na planilha B3:

- 📈 **Ações** (Ações nacionais)
- 🏢 **Fundos Imobiliários** (FIIs)
- 💰 **Renda Fixa** (CDBs, LCIs, LCAs, etc.)
- 🏦 **Tesouro Direto** (Títulos públicos)
- 🌎 **BDRs** (Brazilian Depositary Receipts)
- 📊 **ETFs** (Exchange Traded Funds)
- 🌐 **Ações Internacionais** (Stocks)

## 🔍 Detalhes Técnicos

### Formato da Planilha B3

O aplicativo busca automaticamente as seguintes colunas (com nomes flexíveis):

- **Código/Ticker**: Identificador do ativo (ex: PETR4, MXRF11)
- **Nome/Produto**: Nome completo do ativo
- **Quantidade/Qtd**: Quantidade possuída
- **Preço/Cotação**: Preço unitário
- **Valor Total**: Valor total da posição

### Persistência de Dados

Os seguintes dados são salvos no `localStorage` do navegador:

```javascript
{
  portfolio: {
    assetClasses: { /* dados das classes */ },
    totalValue: 0,
    lastUpdate: "2025-10-28T..."
  },
  targetAllocations: {
    "Ações": 40,
    "FIIs": 20,
    // ...
  },
  yahooFinanceCache: { /* cache de cotações */ }
}
```

### Integração Yahoo Finance (Preparada)

O código já está preparado para integração futura com Yahoo Finance:

```javascript
// Para ações brasileiras, adiciona sufixo .SA
// Exemplo: PETR4 -> PETR4.SA
await fetchYahooFinanceData(ticker, assetClass);
```

**Dados que podem ser obtidos:**
- Cotação atual
- Variação diária (%)
- Volume negociado
- Market Cap
- P/L (Price/Earnings)
- Dividend Yield

## 💡 Dicas de Uso

1. **Mantenha a planilha atualizada**: Importe regularmente sua posição atualizada da B3
2. **Revisão periódica**: Revise sua alocação alvo trimestralmente
3. **Custos de transação**: Considere custos de corretagem ao rebalancear
4. **Imposto de renda**: Lembre-se das implicações fiscais ao vender ativos

## 🔐 Segurança e Privacidade

- ✅ **100% Local**: Todos os dados ficam no seu navegador
- ✅ **Sem servidor**: Nenhum dado é enviado para servidores externos
- ✅ **Código aberto**: Você pode auditar todo o código-fonte
- ⚠️ **Backup**: Recomenda-se fazer backup da planilha original

## 🐛 Solução de Problemas

### A planilha não carrega
- Verifique se o arquivo é `.xlsx` (não `.xls` antigo)
- Confirme que a planilha vem do site da B3
- Tente recarregar a página (F5)

### Dados não aparecem
- Abra o Console do navegador (F12) e verifique erros
- Confirme que a planilha tem dados nas abas
- Limpe o cache: `localStorage.clear()` no console

### Percentuais não batem
- Certifique-se que a soma das alocações é 100%
- Clique em "Salvar Alocação" após ajustar

## 🔄 Próximas Melhorias

- [ ] Integração real com Yahoo Finance API
- [ ] Gráficos de distribuição (Pizza/Barras)
- [ ] Histórico de rebalanceamentos
- [ ] Exportar relatório em PDF
- [ ] Simulador de cenários (What-if)
- [ ] Alertas de rebalanceamento via email
- [ ] Suporte para múltiplas carteiras

## 📝 Licença

Este projeto é de código aberto e livre para uso pessoal.

## 👨‍💻 Desenvolvimento

Para contribuir ou modificar:

```bash
# Clone o repositório
cd investidor

# Faça suas alterações em app.js ou index.html

# Teste localmente
python3 -m http.server 8000

# Abra http://localhost:8000
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção **Solução de Problemas**
2. Revise o código comentado em `app.js`
3. Abra um issue no repositório

---

**Desenvolvido com ❤️ para investidores brasileiros**

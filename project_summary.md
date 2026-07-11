# 🚀 StatusInvest AI Bot & Private SDK
**Documento de Arquitetura e Resumo do Projeto**

## 🎯 Objetivo do Projeto
Criar um ecossistema autônomo, robusto e inteligente para monitorar o mercado financeiro (Ações e FIIs) utilizando os dados do portal StatusInvest. O sistema não apenas extrai indicadores fundamentalistas, mas atua como um "Analista de Investimentos 24/7": ele detecta novos Fatos Relevantes oficiais da CVM e mudanças na Posição Acionária (Insider Trading), lê os documentos, gera resumos executivos usando Inteligência Artificial (LLM Local) e notifica o investidor em tempo real.

---

## 🏗️ Arquitetura e Componentes (Como funciona cada parte)

O projeto foi construído seguindo as melhores práticas de Engenharia de Software (Orientação a Objetos, Injeção de Dependência, Modelagem de Dados Estrita e Tratamento de Exceções).

### 1. O Motor de Busca: `client.py` e `parser.py`
- **`StatusInvestClient`:** É o orquestrador HTTP. Ele sabe exatamente como lidar com a diferença entre Ações e FIIs (usando uma lógica inteligente de *fallback* para erro 404).
- **`StatusInvestParser`:** Usa `BeautifulSoup` para navegar no HTML. Ele foi projetado para "escavar" os dados escondidos pelo site. Ele consegue extrair os PDFs oficiais da CVM que ficam ocultos num JSON dentro da tag `<input name="results">` e as notícias gerais que ficam no `<input id="news-text-hidden">`.
- **Resiliência:** Se o StatusInvest mudar o layout, o Parser lança um `PageLayoutChangedError`, que o sistema captura para avisar você de que o scraper precisa de manutenção, em vez de falhar silenciosamente.

### 2. O Rastreador de Tubarões: `insider.py`
- **`InsiderScraper`:** Um módulo dedicado a rastrear **Insider Trading**. Ele varre a "Posição Acionária" (ex: BNDES, União Federal, Diretoria).
- Se a quantidade de ações ou o percentual de um grande acionista mudar sequer 1%, o módulo detecta a alteração e converte isso em um alerta (lidando ativamente com URLs tanto de Ações quanto de Fundos Imobiliários).

### 3. A Memória (BJSON): `storage.py` e `models/state.py`
- Para evitar que o bot gaste processamento lendo a mesma notícia ou movimentação acionária duas vezes, criamos um **Gerenciador de Estado**.
- Cada evento descoberto (um relatório ou posição acionária) gera uma "impressão digital" única (Hash **MD5**).
- Esse hash é salvo num modelo `Pydantic` e comprimido em disco num arquivo binário ultra-leve usando **`zlib`** (BJSON).
- Na próxima rodada, se o Hash já existir no binário, o robô ignora o evento.

### 4. O Cérebro (IA Local): `ai_analyzer.py`
- Usando a biblioteca **LangChain**, integramos um LLM local (compatível com a API da OpenAI, servido pelo `llama.cpp`).
- Quando um Fato Relevante inédito ou Movimentação Acionária é detectada, o texto bruto é enviado para a IA.
- Utilizamos o recurso `with_structured_output` do LangChain. Isso força a IA a não responder com texto livre, mas sim entregar um objeto de dados exato contendo:
  1. Um **Resumo Executivo** completo (com valores financeiros, justificativas e mudanças operacionais).
  2. Uma **Classificação de Sentimento** (`Positivo`, `Neutro` ou `Negativo`).

### 5. O Mensageiro: `notifier.py`
- Construído com base em **Injeção de Dependências** através de uma interface/classe abstrata mãe (`Notifier`).
- **`TelegramNotifier`:** Para uso em produção. Dispara mensagens ricas em HTML e emojis diretamente no seu celular.
- **`FileNotifier`:** Usado como alternativa de depuração, escrevendo a saída das análises de IA em um arquivo local para debugar o comportamento do modelo local.

### 6. O Maestro: `bot.py`
- O arquivo principal do robô que amarra toda a operação.
- Define a lista de ativos, instancia a injeção do modelo e o Notificador desejado, lê o estado Zlib em memória, rastreia os eventos, submete hashes inéditos à análise inteligente da IA e orquestra todo o fluxo até o Telegram/File log.

---
## 🏁 Conclusão
O SDK é independente e autônomo. Removemos todos os protótipos antigos do repositório para entregar uma solução 100% focada, mantendo o diretório principal elegante, configurável por variáveis de ambiente (`.env`), e estruturado para escalabilidade extrema com Inteligência Artificial.

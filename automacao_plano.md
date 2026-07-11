# 🗓️ Plano de Automação: StatusInvest AI Bot

Este documento define a arquitetura e os passos necessários para colocar o seu robô rodando de forma 100% autônoma, orquestrando a subida da inteligência artificial, a raspagem e o desligamento da máquina.

## 1. Variáveis de Ambiente (Implementado ✅)
O código já foi atualizado para não depender mais de ativos *hardcoded*. O bot agora consome os ativos direto do ambiente.

Para configurar, basta adicionar ao `.env`:
```env
ATIVOS_MONITORADOS="PETR4,TAEE11,XPML11,VALE3,ITUB4"
```

---

## 2. Orquestração: O Script Principal (`pipeline.sh` ou `pipeline.bat`)

Em vez de agendar comandos separados, criaremos um único script (Shell Script no Linux/WSL ou Batch no Windows) que fará a orquestração sequencial. Ele atuará como o maestro do processo:

```bash
#!/bin/bash

# Passo 1: Subir o Servidor LLM (Interface abstrata)
echo "Iniciando o servidor do Llama..."
llama_up &
LLM_PID=$!

# Aguarda alguns segundos para o servidor subir completamente na porta 8080
sleep 15

# Passo 2: Rodar o Bot
echo "Iniciando raspagem e análise de IA..."
cd /caminho/para/o/projeto/investidor
uv run python bot.py

# Passo 3: Limpeza (Opcional, mas recomendado)
echo "Derrubando o servidor LLM local..."
kill $LLM_PID

# Passo 4: Desligar o computador (Interface abstrata)
echo "Desligando a máquina..."
win-shutdown
```

> [!TIP]
> Se esse comando rodar diretamente do Windows (cmd/Powershell) via WSL, o `win-shutdown` pode ser substituído concretamente por `shutdown /s /f /t 10`.

---

## 3. Agendamento Automático (Cron Job ou Agendador de Tarefas)

Precisamos que esse fluxo rode sem intervenção humana, preferencialmente após o fechamento do mercado (ex: 19:00).

**Se você for usar WSL/Linux (Cron):**
Basta abrir o crontab (`crontab -e`) e adicionar a seguinte linha para rodar de segunda a sexta às 19:00:
```cron
0 19 * * 1-5 /bin/bash /caminho/para/o/pipeline.sh >> /caminho/para/logs/cron.log 2>&1
```

**Se você for usar o Windows Nativo (Agendador de Tarefas):**
1. Abra o **Task Scheduler** (Agendador de Tarefas).
2. Crie uma Tarefa Básica: *"Executar Bot StatusInvest"*.
3. Defina o gatilho para **Diariamente**, configurando o horário desejado (ex: 19h).
4. Na aba **Ação**, mande iniciar um programa e aponte para o seu script `.bat` equivalente.
5. Em **Condições**, marque para ligar o computador (se aplicável) e rodar caso não esteja em uso.

---

## 4. O Fluxo de Vida Desejado (TL;DR)

1. **Relógio bate 19:00** 🕒
2. Cron/Agendador chama o `pipeline`.
3. Máquina carrega o `llama_up` na memória (porta 8080).
4. Bot coleta URLs CVM na nuvem.
5. Bot faz download de Fatos Relevantes e extrai formulários de "Posição Acionária".
6. Bot envia o PDF cru + HTML ao LLM ativo.
7. O Telegram do Investidor apita com os resumos mastigados.
8. Máquina aciona o comando `win-shutdown` e descansa até o dia seguinte. 💤

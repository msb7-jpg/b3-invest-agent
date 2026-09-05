# 🗓️ Automation Plan: StatusInvest AI Bot & IoT Lifecycle

This document defines the architecture and automation procedures required to operate the bot completely autonomously, integrating smart home hardware (Amazon Alexa), scheduled local AI inference (`llama.cpp`), and automated machine power management.

---

## 1. Environment Configuration (.env)

The bot dynamically loads monitored assets from the environment:

```env
ATIVOS_MONITORADOS="PETR4,TAEE11,XPML11,VALE3,ITUB4"
OPENAI_API_BASE="http://localhost:8080/v1"
OPENAI_API_KEY="not-needed"
OPENAI_MODEL_NAME="local-model"
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
```

---

## 2. Infrastructure & Hardware Lifecycle (Amazon Alexa Routine)

To achieve maximum energy efficiency (0W idle standby) without paying for 24/7 cloud servers:

1. **03:45 AM (Smart Turn-On)**:
   - Amazon Alexa triggers a routine using a Smart Plug (or Wake-on-LAN) to boot the home desktop workstation.
   - Operating system and networking services initialize.
2. **04:45 AM (Smart Turn-Off)**:
   - Exactly 1 hour after startup, the Alexa routine sends a graceful shutdown command or cuts power via the Smart Plug timer, leaving the computer safely powered off for the rest of the day.

---

## 3. Orchestration Script (`pipeline.sh`)

Place `pipeline.sh` in the project root to orchestrate starting the local LLM, executing the bot, and cleaning up:

```bash
#!/bin/bash
set -e

PROJECT_DIR="/home/miguel/workspace/investidor"
cd "$PROJECT_DIR"

echo "[$(date)] Starting local llama.cpp server..."
# Example: starting llama.cpp server in the background
# ./llama-server -m /models/mistral-7b-instruct.Q4_K_M.gguf --port 8080 --ctx-size 4096 &
llama_up &
LLM_PID=$!

# Wait 15 seconds for the HTTP API to become ready on port 8080
sleep 15

echo "[$(date)] Executing StatusInvest Bot..."
uv run python bot.py

echo "[$(date)] Stopping local LLM server (PID: $LLM_PID)..."
kill $LLM_PID || true

echo "[$(date)] Processing finished successfully."
```

Make it executable:
```bash
chmod +x pipeline.sh
```

---

## 4. Crontab Scheduling (03:50 AM)

Configure Linux `crontab` (`crontab -e`) to trigger 5 minutes after desktop boot:

```cron
# Runs Monday through Friday at 03:50 AM
50 3 * * 1-5 /home/miguel/workspace/investidor/pipeline.sh >> /home/miguel/workspace/investidor/logs/cron.log 2>&1
```

---

## 5. End-to-End Operational Lifecycle (TL;DR)

1. **03:45 AM** 🕒: Alexa routine triggers hardware boot (Smart Plug / WoL).
2. **03:50 AM** ⏰: Crontab initiates `pipeline.sh`.
3. **03:50 AM** 🦙: `llama.cpp` loads the local model into VRAM/RAM on port 8080.
4. **03:51 AM** 📡: `bot.py` queries StatusInvest and CVM for new Material Facts & Insider Positions.
5. **03:52 AM** 💾: State Manager deduplicates filings via MD5 hashes in `data/state.zlib`.
6. **03:53 AM** 🧠: Unseen reports are analyzed by the local LLM (sentiment + executive summary).
7. **03:55 AM** 📲: Rich HTML market alerts are dispatched via Telegram Bot API to the investor.
8. **04:45 AM** 💤: Alexa routine safely powers off the workstation after the 1-hour window.

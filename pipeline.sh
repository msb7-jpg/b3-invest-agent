#!/bin/bash
# ==============================================================================
# Pipeline Execution Script: StatusInvest AI Bot & Local LLM
# Triggered via crontab at 03:50 AM after Alexa powers on the desktop.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting pipeline execution..."

# 1. Start local LLM server if not already running
# Customize command below for your local llama.cpp / llama-server setup:
if command -v llama_up >/dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting llama.cpp via llama_up..."
    llama_up &
    LLM_PID=$!
    sleep 15
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] llama_up alias not found; assuming llama.cpp server is running on port 8080."
fi

# 2. Run the bot
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running StatusInvest bot..."
uv run python bot.py

# 3. Clean up LLM server if spawned here
if [ -n "$LLM_PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Stopping local LLM server (PID: $LLM_PID)..."
    kill "$LLM_PID" || true
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pipeline completed successfully."

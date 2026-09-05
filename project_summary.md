# 🚀 StatusInvest AI Bot & Private SDK
**Architecture Document & Project Summary**

## 🎯 Project Objective
Build an autonomous, robust, and intelligent ecosystem to monitor the Brazilian financial market (Stocks and REITs / FIIs) leveraging data from the StatusInvest platform. The system does not merely extract fundamental indicators; it operates as a "24/7 Investment Analyst": it detects official CVM Material Facts and Shareholding Changes (Insider Trading), reads regulatory documents, generates executive summaries using Local AI (LLM), and notifies the investor in real time.

---

## 🏗️ Architecture & Components (How each part works)

The project follows software engineering best practices (Object-Oriented Design, Dependency Injection, Strict Data Modeling, and Resilient Exception Handling).

### 1. Data Ingestion Engine: `client.py` and `parser.py`
- **`StatusInvestClient`:** The core HTTP orchestrator. It handles the nuances between Stocks and REITs (using intelligent 404 fallback logic).
- **`StatusInvestParser`:** Utilizes `BeautifulSoup` to navigate the DOM. Designed to unearth data embedded in the portal. It extracts official CVM PDFs concealed within JSON inside the `<input name="results">` tag and general announcements inside `<input id="news-text-hidden">`.
- **Resilience:** If StatusInvest changes its HTML DOM layout, the parser raises `PageLayoutChangedError`, allowing the system to alert the maintainer rather than silently failing.

### 2. Insider Tracker: `insider.py`
- **`InsiderScraper`:** A dedicated module for tracking **Insider Trading**. It monitors "Shareholding Positions" (e.g., government stakes, pension funds, board members, controllers).
- If share count or ownership percentage changes even by 1%, the module detects the modification and triggers an alert (seamlessly handling both Stock and REIT endpoints).

### 3. State Memory (BJSON): `storage.py` and `models/state.py`
- To prevent redundant LLM inference on already processed reports or ownership updates, we implemented a **State Manager**.
- Each detected event (a filing or stake change) receives a unique fingerprint (**MD5** hash).
- This hash is stored in a `Pydantic` model and compressed to disk as an ultra-compact binary file using **`zlib`** (BJSON).
- On subsequent runs, if the hash exists in the state store, the event is skipped.

### 4. Intelligence Engine (Local AI): `ai_analyzer.py`
- Powered by **LangChain**, integrating a local LLM (OpenAI API-compatible, served via `llama.cpp`, `LM Studio`, or `Ollama`).
- When a new Material Fact or Insider Movement is detected, raw text is sent to the LLM.
- We utilize LangChain's `with_structured_output`, strictly enforcing structured Pydantic objects containing:
  1. A comprehensive **Executive Summary** (financial numbers, rationale, operational impacts).
  2. A **Sentiment Classification** (`Positive`, `Neutral`, or `Negative`).

### 5. Notification Dispatcher: `notifier.py`
- Built around **Dependency Injection** via an abstract base class (`Notifier`).
- **`TelegramNotifier`:** Production dispatcher delivering rich HTML messages directly to mobile devices.
- **`FileNotifier`:** Debugging alternative logging AI analyses locally to inspect model prompt outputs.

### 6. Orchestrator: `bot.py`
- The main bot runtime tying together the entire pipeline.
- Loads monitored tickers, configures dependency injection for AI and Notifiers, manages the compressed Zlib state, queries updates, passes unseen events to AI analysis, and routes alerts to Telegram / debug logs.

---

## 🏁 Conclusion
The SDK is fully autonomous and decoupled. The repository is configured via environment variables (`.env`), structured for high reliability, and designed for scalable local AI operations.

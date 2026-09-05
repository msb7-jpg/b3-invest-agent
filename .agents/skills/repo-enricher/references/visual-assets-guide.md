# Visual Assets & Placeholder Guide

Recruiters spend an average of 6–10 seconds glancing at a GitHub repository before deciding whether to read deeper or contact the candidate. Clear visuals, badges, diagrams, and structured screenshot placeholders immediately establish professional polish.

---

## 🛡️ 1. Dynamic Shields.io Badges

Place these directly under the main `# Title` in a centered `<div>`:

```markdown
<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.3+-green.svg?style=for-the-badge&logo=chainlink&logoColor=white)](https://www.langchain.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-e92063.svg?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg?style=for-the-badge&logo=pytest&logoColor=white)](./tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg?style=for-the-badge)](./LICENSE)

</div>
```

---

## 🖼️ 2. Formatting Image & Demo Placeholders

When screenshots or demo recordings are not ready yet, **never leave a blank gap**. Use styled HTML placeholder callouts that make it effortless to drop images in later.

### Pattern A: Hero Showcase Placeholder (Centered with shadow)

```markdown
<div align="center">
  <img src="docs/assets/banner_or_demo.png" alt="System Overview Showcase" width="850px" style="border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);" />
  <p><i>📸 <b>Demo Placeholder</b>: Replace with screen recording (GIF/MP4) showing the bot executing and streaming Telegram alerts.</i></p>
</div>
```

### Pattern B: Multi-Screenshot Gallery Table

```markdown
| 📲 Mobile Notification | 💻 Terminal Execution & Local LLM |
| :---: | :---: |
| <img src="docs/assets/telegram_sample.png" alt="Telegram Notification" width="360px" /> | <img src="docs/assets/terminal_output.png" alt="Terminal Run" width="460px" /> |
| *Real-time executive briefing on Telegram* | *Autonomous batch run via `llama.cpp`* |
```

---

## 📊 3. Mermaid Diagram Best Practices for GitHub

GitHub natively renders Mermaid code fences (` ```mermaid `). Follow these rules to avoid parsing failures:

1. **Always wrap node text with double quotes `["..."]`** whenever text contains parentheses, slashes, colons, or punctuation.
2. **Never put bare pipe characters (`|`) inside node text.** Use `<br/>` for line breaks and `/` or `or` instead of `|`.
3. **Use subgraphs to separate architectural concerns**:
   - `Ingestion` / `Sensors`
   - `Storage` / `State`
   - `Reasoning` / `LLM`
   - `Output` / `Delivery`

### Example:

```mermaid
flowchart TD
    subgraph Data ["📡 Data Layer"]
        A["External Portal / API"] --> B["Ingestion Engine"]
    end
    
    subgraph Logic ["🧠 Logic & Model"]
        B --> C[("Local State Cache")]
        B --> D["Local LLM Server<br/>(llama.cpp)"]
    end
    
    subgraph UI ["📱 User Output"]
        D --> E["Telegram Bot API"]
    end
```

---

## 🚀 4. How to Host & Upload Assets to GitHub

1. **In-Repo Directory (Recommended for Portfolios)**:
   ```bash
   mkdir -p docs/assets
   # Copy your screenshots here:
   # cp /path/to/screenshot.png docs/assets/demo.png
   # git add docs/assets && git commit -m "docs: add demo screenshots"
   ```
2. **Direct Markdown Embedding**:
   Reference with relative paths: `![Demo](docs/assets/demo.png)`.
   This ensures images render offline, in GitHub web, and across forks.

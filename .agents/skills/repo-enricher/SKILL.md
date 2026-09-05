---
name: repo-enricher
description: >-
  Comprehensive guide and automation standard for enriching GitHub repository metadata,
  SEO keywords, topics, and READMEs to maximize recruiter impact. Uses the GitHub CLI (gh)
  to optimize descriptions and tags, and restructures READMEs with Shields.io badges,
  Mermaid system architecture diagrams, quantifiable impact metrics, and visual screenshot placeholders.
---

# 🚀 GitHub Repo Enricher & Recruiter Showcase Skill

This skill provides an end-to-end framework and automated procedures to elevate any GitHub repository into a high-impact portfolio asset that impresses technical recruiters, engineering managers, and open-source visitors within the critical first 10 seconds of evaluation.

---

## 🧭 Recruiter-Centric Philosophy

Technical recruiters and hiring managers do not have time to read thousands of lines of source code. They look for:
1. **Instant Clarity (0–5s)**: A clear headline and dynamic badges showing modern tech stack (e.g., Python 3.13+, LangChain, Pydantic, uv, Docker).
2. **Visual Proof & Architecture (5–15s)**: Clear Mermaid system design diagrams and screenshot/demo placeholders showing what was built.
3. **Business & Engineering Impact (15–30s)**: Quantifiable outcomes using the STAR method (e.g., "reduced latency by 80%", "zero cloud API cost", "100% test coverage").
4. **Seniority & Trade-Offs (30s+)**: Explicit discussion of why architectural choices were made (e.g., Local LLM vs Cloud API, Zlib state vs Postgres).

---

## 🛠️ Step-by-Step Optimization Workflow

### Phase 1: Audit Current Repository Readiness
Run the bundled audit script to assess missing metadata, topics, diagrams, and metrics:

```bash
./.agents/skills/repo-enricher/scripts/audit_repo.sh
```

---

### Phase 2: Enrich GitHub Metadata with `gh` CLI

Apply the headline formula and high-value topics from [references/keyword-taxonomy.md](./references/keyword-taxonomy.md):

1. **Craft a High-Signal Description (Max 350 chars)**:
   - Must include: Primary Role/Artifact + Core Problem + Main Tech Stack + Delivery/Benefit.
   - Example:
     ```bash
     gh repo edit \
       --description "🤖 Autonomous AI Agent & Python SDK for B3 market intelligence via StatusInvest. CVM material facts monitoring, insider trading tracking, and zero-cost local LLM inference (llama.cpp) with Telegram alerts."
     ```

2. **Add 10–15 Targeted Industry Topics**:
   - Combine core language + specialized framework + domain/role + key concepts:
     ```bash
     gh repo edit \
       --add-topic "ai-agent,autonomous-agents,langchain,llm,local-llm,llama-cpp,pydantic,python,statusinvest,b3,financial-analysis,investments,web-scraping,telegram-bot"
     ```

3. **Helper Automation**:
   Use the non-interactive script to apply both in one command:
   ```bash
   ./.agents/skills/repo-enricher/scripts/update_metadata.sh \
     --desc "Autonomous AI Agent for Market Intelligence" \
     --topics "ai-agent,langchain,python,finance"
   ```

---

### Phase 3: Revamp README for Maximum Recruiter Conversion

Follow the structural standard in [references/recruiter-readme-template.md](./references/recruiter-readme-template.md):

#### 1. Hero Badges & Header
- Insert Shields.io badges for: Python/Node version, Core framework (LangChain/FastAPI), Test status, Package manager (`uv`/`poetry`), and License.
- Add an executive one-liner.

#### 2. Business Impact & The Problem Solved (STAR Framework)
- **Situation**: What manual inefficiency existed?
- **Action**: How does the system solve it autonomously?
- **Result**: Quantifiable metrics (e.g., 8/8 tests passing, 0W idle power, $0 API bill).

#### 3. Architecture Diagrams (Mermaid)
- Always include at least one **System Architecture Flowchart** and one **End-to-End Sequence Diagram**.
- Guidelines from [references/visual-assets-guide.md](./references/visual-assets-guide.md):
  - Always quote node text with `["..."]`.
  - Use `<br/>` for line breaks.
  - Never place unquoted pipe characters (`|`) inside node text.

#### 4. Visual Proof & Image Placeholders
- Add structured screenshot placeholders so recruiters see what the UI/CLI looks like, even before screenshots are uploaded:
  ```markdown
  | 📲 Mobile Briefing | 🖥️ Local AI Inference (CLI) |
  | :---: | :---: |
  | <img src="docs/assets/telegram_alert.png" alt="Telegram Notification" width="360px" /> | <img src="docs/assets/cli_run.png" alt="CLI Execution" width="460px" /> |
  | *Executive market digest on Telegram* | *Batch local inference with llama.cpp* |
  
  > [!NOTE]
  > **Screenshots Placeholder**: Save `.png` captures to `docs/assets/` to display live previews.
  ```

#### 5. Senior Engineering Decisions (Trade-Offs)
- Detail 2–3 architectural decisions explaining *why* technology X was chosen over Y (e.g., Memory efficiency of binary state vs SQL, Local LLM vs Cloud API).

#### 6. Frictionless Quickstart
- Provide copy-pasteable, verified CLI commands (`git clone`, `uv sync`, `uv run pytest`, `uv run python main.py`).

---

## 🛡️ Best Practices & Quality Checklist

Before finalizing any repository enrichment:
- [ ] `gh auth status` verified.
- [ ] `gh repo view` confirms description is < 350 chars with relevant keywords.
- [ ] At least 8-12 relevant topics added (in English, hyphenated).
- [ ] All Mermaid diagrams validated without parsing errors.
- [ ] Visual placeholders include clear user instructions for where to paste images (`docs/assets/`).
- [ ] Tech stack badges render properly via Shields.io.
- [ ] All test and build commands are fully reproducible.

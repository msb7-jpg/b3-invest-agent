---
name: gh-cli
description: Comprehensive guide and automation standard for interacting with the GitHub CLI (`gh`) agnostically across any repository. Covers non-interactive execution, repository metadata discovery, pull requests, issues, releases, GitHub Actions (CI/CD), and REST/GraphQL API queries with structured JSON output. Activate this skill whenever the user or agent needs to run `gh` commands, manage repositories on GitHub, inspect CI runs, create PRs, or update repo metadata.
---

# GitHub CLI (`gh`) Agnostic Automation Skill

Esta skill define as melhores práticas, padrões de execução não-interativa e comandos essenciais para interagir com o GitHub CLI (`gh`) de forma **100% agnóstica a qualquer repositório**, sem depender de nomes fixos de repositório ou branch.

---

## 🧭 Princípios Fundamentais de Uso Agnóstico

1. **Descoberta Automática de Contexto**:
   - Em qualquer pasta versionada pelo Git, o `gh` descobre o repositório atual a partir da URL do remote `origin` (`git config --get remote.origin.url`).
   - **Nunca** passe `owner/repo` fixo no comando quando estiver dentro da pasta do projeto. O `gh` atua automaticamente sobre o repositório local.
   - Para obter os dados do repositório atual programaticamente:
     ```bash
     gh repo view --json name,nameWithOwner,defaultBranchRef,visibility
     ```

2. **Execução 100% Não-Interativa (Zero Prompts)**:
   - Para uso por agentes de IA e scripts CI/CD, comandos como `gh pr create` e `gh issue create` **nunca** devem solicitar inputs no terminal.
   - Forneça sempre todos os argumentos obrigatórios:
     - `gh pr create --title "..." --body "..." --base <branch> --head <branch>` (ou use `--fill`).
     - `gh issue create --title "..." --body "..."`.

3. **Respostas Estruturadas em JSON (`--json` e `--jq`)**:
   - Nunca faça scraping de tabelas de texto plano no terminal.
   - Use `--json <campos>` combinado com `--jq '<filtro>'` para extrair variáveis limpas diretamente no shell.
   - Exemplo:
     ```bash
     DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q '.defaultBranchRef.name')
     ```

4. **Resolução Mágica de Placeholders na API REST**:
   - O comando `gh api` aceita `{owner}` e `{repo}` diretamente na URL, substituindo-os automaticamente pelos valores do repositório local:
     ```bash
     gh api repos/{owner}/{repo}/collaborators
     ```

---

## 🛠️ Subdocumentos e Utilitários da Skill

Consulte a documentação modular desta skill para consultas aprofundadas:

- **Script de Inspeção Rápida**: [scripts/repo_info.sh](./scripts/repo_info.sh) (Extrai metadados completos em JSON).
- **Tabela Completa de Comandos**: [references/commands-cheatsheet.md](./references/commands-cheatsheet.md) (Auth, Repo, PR, Issue, CI, Release, Secrets).
- **Receitas de Automação para Agentes**: [references/automation-recipes.md](./references/automation-recipes.md) (Fluxos ponta-a-ponta de PR, triagem de falhas de CI e atualização de metadados).

---

## ⚡ Fluxos Rápidos Mais Comuns

### 1. Inspecionar o Repositório Atual
```bash
# Executa o utilitário embutido da skill
./.agents/skills/gh-cli/scripts/repo_info.sh
```

### 2. Atualizar Metadados de Portfólio (Descrição e Tópicos)
```bash
gh repo edit \
  --description "Descrição concisa e profissional do projeto" \
  --add-topic "python,ai,langchain,automation"
```

### 3. Abrir Pull Request Automaticamente
```bash
gh pr create \
  --title "feat: implementação da funcionalidade X" \
  --body "Detalhes das alterações realizadas." \
  --base "$(gh repo view --json defaultBranchRef -q '.defaultBranchRef.name')"
```

### 4. Depurar Pipelines do GitHub Actions
```bash
# Ver últimos runs e logs de falhas
gh run list --limit 5
gh run view --log-failed
```

---

## 🛡️ Checklist de Verificação antes de Executar

- [ ] `gh auth status` executado para validar se o usuário está logado e possui escopo `repo`.
- [ ] Diretório atual verificado como repositório Git com remote válido.
- [ ] Todas as flags de título e corpo informadas em comandos de criação (evitando travas interativas).
- [ ] Saídas tratadas via JSON para garantir robustez e portabilidade entre sistemas.

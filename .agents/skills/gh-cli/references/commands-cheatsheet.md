# 📖 GitHub CLI (`gh`) Agnostic Commands Cheatsheet

Este guia reúne os principais comandos do `gh` formatados para execução **não-interativa** e **agnóstica a repositório**. Quando executado dentro de qualquer diretório clonado com `git remote origin`, o `gh` infere automaticamente o repositório atual sem necessidade de passar `owner/repo`.

---

## 1. Autenticação & Contexto

```bash
# Verificar status da autenticação, scopes e usuário logado
gh auth status

# Obter o token atual (útil para passar como header ou testar chamadas)
gh auth token

# Configurar protocolo git para usar credenciais do gh CLI
gh auth setup-git
```

---

## 2. Repositórios (`gh repo`)

```bash
# Ver metadados do repositório atual em JSON (sem hardcode)
gh repo view --json name,nameWithOwner,description,homepageUrl,visibility,repositoryTopics,defaultBranchRef

# Extrair apenas campos específicos usando --jq
gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'
gh repo view --json isPrivate -q '.isPrivate'

# Alterar descrição e tópicos/tags
gh repo edit --description "Nova descrição do repositório" --add-topic "python,automation,ai"

# Alterar página inicial e habilitar issues/discussions
gh repo edit --homepage "https://meuprojeto.dev" --enable-issues --enable-wiki=false

# Clonar ou fazer fork (agnóstico)
gh repo clone <owner>/<repo>
gh repo fork --clone=false --remote=true

# Sincronizar fork com o upstream
gh repo sync
```

---

## 3. Pull Requests (`gh pr`)

> **Importante para Automação:** Sempre forneça `--title` e `--body` (ou `--fill`) para evitar que o comando abra um editor interativo.

```bash
# Listar PRs abertos com campos estruturados em JSON
gh pr list --state open --json number,title,author,headRefName,baseRefName,updatedAt

# Ver detalhes do PR atual da branch
gh pr view --json number,title,state,mergeable,reviews

# Ver o diff completo de um PR
gh pr diff [pr_number]

# Criar um PR de forma totalmente não-interativa
gh pr create --title "feat: adiciona nova funcionalidade" \
             --body "Descrição detalhada das mudanças realizadas." \
             --base main

# Criar PR preenchendo automaticamente título e corpo com commits da branch
gh pr create --fill

# Fazer checkout local da branch de um PR
gh pr checkout <pr_number>

# Adicionar review/aprovação
gh pr review <pr_number> --approve -b "LGTM! Testes passaram."
gh pr review <pr_number> --comment -b "Por favor verificar tratamento de erro na linha 42."

# Fazer merge do PR (com exclusão da branch e squash)
gh pr merge <pr_number> --squash --delete-branch --auto
```

---

## 4. Issues (`gh issue`)

```bash
# Listar issues abertas formatadas em JSON
gh issue list --state open --limit 20 --json number,title,labels,author,createdAt

# Criar uma issue não-interativa
gh issue create --title "bug: erro ao carregar variáveis de ambiente" \
                --body "Passos para reproduzir: ..." \
                --label "bug,triage"

# Ver uma issue em formato markdown ou JSON
gh issue view <issue_number>
gh issue view <issue_number> --json title,body,comments,state

# Comentar em uma issue
gh issue comment <issue_number> --body "Correção enviada no PR #12."

# Fechar uma issue
gh issue close <issue_number> --reason "completed"
```

---

## 5. GitHub Actions & CI/CD (`gh run` & `gh workflow`)

```bash
# Listar execuções recentes de pipelines CI/CD
gh run list --limit 10 --json databaseId,status,conclusion,workflowName,headBranch,event

# Inspecionar detalhes de uma execução específica
gh run view <run_id>

# Baixar e inspecionar logs de erro de uma execução que falhou
gh run view <run_id> --log-failed

# Aguardar a finalização de uma execução em tempo real
gh run watch <run_id>

# Disparar novamente uma execução com falha
gh run rerun <run_id> --failed

# Disparar um workflow manual (workflow_dispatch)
gh workflow run ci.yml --ref main -f environment=staging
```

---

## 6. Releases & Tags (`gh release`)

```bash
# Listar releases existentes
gh release list

# Criar uma release com geração automática de changelog / release notes
gh release create v1.0.0 --title "v1.0.0 - Lançamento Inicial" --generate-notes

# Criar uma release anexando binários ou arquivos compilados
gh release create v1.0.0 dist/* --title "Release v1.0.0" --notes "Release estável."

# Baixar assets de uma release
gh release download v1.0.0 -D ./downloads
```

---

## 7. Chamadas Diretas à API (`gh api`)

O comando `gh api` substitui `curl` autenticado e resolve magicamente os placeholders `{owner}` e `{repo}` para o repositório atual:

```bash
# Consultar informações do repositório atual via REST API (agnóstico!)
gh api repos/{owner}/{repo}

# Consultar branches protegidas
gh api repos/{owner}/{repo}/branches

# Disparar requisição POST (ex: disparar um dispatch event)
gh api repos/{owner}/{repo}/dispatches -X POST -f event_type='deploy_trigger'

# Consultar rate limit da API do GitHub
gh api rate_limit -q '.rate'
```

---

## 8. Variáveis e Secrets (`gh secret` / `gh variable`)

```bash
# Listar secrets cadastrados (nomes apenas, valores são protegidos)
gh secret list

# Definir um secret no repositório atual
gh secret set API_KEY --body "meu_valor_secreto"

# Definir a partir de um arquivo .env
gh secret set -f .env

# Variáveis não-secretas de ambiente
gh variable list
gh variable set ENVIRONMENT --body "production"
```

# 🛠️ GitHub CLI Automation Recipes for AI Agents

Este documento contém receitas práticas de automação para agentes e scripts que interagem com o `gh` de forma autônoma, segura e sem intervenção humana.

---

## Receita 1: Diagnóstico e Descoberta Agnóstica do Repositório

Antes de executar qualquer mutação, descubra o contexto sem presumir nomes de branch ou repositório:

```bash
# 1. Verificar se o gh está autenticado
gh auth status > /dev/null 2>&1 || { echo "gh não autenticado!"; exit 1; }

# 2. Obter informações consolidadas do repositório em formato JSON
REPO_JSON=$(gh repo view --json nameWithOwner,defaultBranchRef,visibility,isFork)
REPO_NAME=$(echo "$REPO_JSON" | jq -r '.nameWithOwner')
DEFAULT_BRANCH=$(echo "$REPO_JSON" | jq -r '.defaultBranchRef.name')
IS_PRIVATE=$(echo "$REPO_JSON" | jq -r '.visibility == "PRIVATE"')

echo "Repositório: $REPO_NAME | Branch Padrão: $DEFAULT_BRANCH | Privado: $IS_PRIVATE"
```

---

## Receita 2: Fluxo Completo de Criação e Merge de Pull Request

Para criar PRs sem travar o terminal esperando interação:

```bash
BRANCH_NAME="feature/melhoria-$(date +%s)"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q '.defaultBranchRef.name')

# 1. Criar branch e comitar alterações
git checkout -b "$BRANCH_NAME"
git add .
git commit -m "feat: adiciona melhoria automatizada"

# 2. Fazer push configurando upstream
git push -u origin "$BRANCH_NAME"

# 3. Abrir PR com flags completas (título, corpo, base e head)
PR_URL=$(gh pr create \
  --title "feat: adiciona melhoria automatizada" \
  --body "### Resumo das Mudanças\n- Atualização de arquivos de configuração\n- Ajustes automatizados pelo assistente." \
  --base "$DEFAULT_BRANCH" \
  --head "$BRANCH_NAME")

echo "Pull Request criado com sucesso: $PR_URL"

# 4. (Opcional) Habilitar auto-merge após CI passar
gh pr merge "$PR_URL" --auto --squash --delete-branch
```

---

## Receita 3: Diagnosticar Falhas de CI em Tempo Real

Quando um teste ou pipeline do GitHub Actions falha, extraia os logs exatos do erro programaticamente:

```bash
# 1. Identificar a última execução com falha da branch atual
FAILED_RUN_ID=$(gh run list --branch "$(git rev-parse --abbrev-ref HEAD)" \
                            --status failure \
                            --limit 1 \
                            --json databaseId \
                            -q '.[0].databaseId')

if [ -n "$FAILED_RUN_ID" ] && [ "$FAILED_RUN_ID" != "null" ]; then
  echo "Inspecionando falha da Run ID: $FAILED_RUN_ID"
  
  # 2. Extrair apenas as linhas do log onde houve falha
  gh run view "$FAILED_RUN_ID" --log-failed | tail -n 50
else
  echo "Nenhuma falha recente encontrada nesta branch."
fi
```

---

## Receita 4: Padronização de Metadados de Portfólio

Para atualizar descrições, tópicos e metadados de vitrine em lote:

```bash
# Define descrição profissional e tópicos relevantes
gh repo edit \
  --description "Descrição concisa, clara e focada no valor do projeto" \
  --add-topic "python,ai,automation,fastapi,clean-architecture" \
  --enable-issues=true \
  --enable-wiki=false
```

---

## ⚠️ Regras Críticas de Segurança para Agentes

1. **Nunca exponha tokens de autenticação**: O comando `gh auth token` exibe o token em texto puro; nunca direcione sua saída para commits, arquivos de log versionados ou mensagens visíveis para terceiros.
2. **Sempre use `--json` e `--jq`**: Evite `grep` e `awk` na saída tabular padrão do `gh`, pois a formatação de colunas varia conforme o tamanho do terminal.
3. **Evite comandos interativos**: Se você omitir `--title` e `--body` em `gh pr create` ou `gh issue create`, o `gh` abrirá o `nano` ou `vim`, travando o processo de execução em segundo plano.
4. **Verifique permissões antes de mutações destrutivas**: Use `gh repo view --json viewerPermission` para verificar se o usuário atual tem permissão de escrita (`WRITE` ou `ADMIN`).

#!/usr/bin/env bash
# ==============================================================================
# Repository Recruiter-Readiness Audit Script
# Agnostically audits current repository metadata and README quality for recruiters.
# Uses native gh CLI -q filtering (zero dependency on external jq).
# ==============================================================================
set -euo pipefail

echo "============================================================"
echo " 🔍 Auditing Repository for Recruiter Impact"
echo "============================================================"

# 1. Verify git repository and gh CLI authentication
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Error: Not inside a Git repository."
    exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "❌ Error: 'gh' CLI is not installed or not in PATH."
    exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "❌ Error: 'gh' is not authenticated. Run 'gh auth login'."
    exit 1
fi

# 2. Extract GitHub metadata using native gh -q
FULL_NAME=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
DESC=$(gh repo view --json description -q '.description // ""')
TOPICS=$(gh repo view --json repositoryTopics -q '[.repositoryTopics[].name] | join(", ")')
TOPICS_COUNT=$(gh repo view --json repositoryTopics -q '.repositoryTopics | length')

echo "📦 Repository:   $FULL_NAME"
echo "📝 Description:  ${DESC:-"(EMPTY - Needs optimization)"}"
echo "🏷️  Topics ($TOPICS_COUNT):   ${TOPICS:-"(NONE - Needs high-value keywords)"}"

# 3. Audit README.md
README_FILE=""
for f in README.md readme.md Readme.md; do
    if [ -f "$f" ]; then
        README_FILE="$f"
        break
    fi
done

echo "------------------------------------------------------------"
echo " 📄 README Assessment"
echo "------------------------------------------------------------"

if [ -z "$README_FILE" ]; then
    echo "❌ README.md is MISSING! High priority fix needed."
    exit 0
fi

echo "✅ README found: $README_FILE"

# Checks
HAS_BADGES=$(grep -qE 'img\.shields\.io' "$README_FILE" && echo "YES" || echo "NO")
HAS_MERMAID=$(grep -qF '```mermaid' "$README_FILE" && echo "YES" || echo "NO")
HAS_IMAGES=$(grep -qE '!\[.*\]\(.*\)' "$README_FILE" && echo "YES" || echo "NO")
HAS_PLACEHOLDERS=$(grep -qE '(PLACEHOLDER|Insert screenshot here|your_screenshot|<img)' "$README_FILE" && echo "YES" || echo "NO")
HAS_METRICS=$(grep -qE '([0-9]+%|[0-9]+ms|[0-9]+x|Passed|Coverage)' "$README_FILE" && echo "YES" || echo "NO")
WORD_COUNT=$(wc -w < "$README_FILE")

echo " - Shields Badges:      $HAS_BADGES"
echo " - Mermaid Diagrams:    $HAS_MERMAID"
echo " - Visuals/Images:      $HAS_IMAGES"
echo " - Image Placeholders:  $HAS_PLACEHOLDERS"
echo " - Quantified Metrics:  $HAS_METRICS"
echo " - Word Count:          $WORD_COUNT words"

echo "------------------------------------------------------------"
echo " 🎯 Recommendations Summary"
echo "------------------------------------------------------------"
[ -z "$DESC" ] && echo " ⚠️ Add a keyword-rich description (350 chars max) with 'gh repo edit -d \"...\"'"
[ "$TOPICS_COUNT" -lt 5 ] && echo " ⚠️ Add at least 5-10 relevant industry topics with 'gh repo edit --add-topic \"...\"'"
[ "$HAS_BADGES" = "NO" ] && echo " ⚠️ Add Shields.io badges for tech stack, version, test status, and license."
[ "$HAS_MERMAID" = "NO" ] && echo " ⚠️ Add at least 1 Mermaid architecture or data-flow diagram."
[ "$HAS_IMAGES" = "NO" ] && echo " ⚠️ Add UI/CLI screenshots or placeholders to demonstrate execution."
[ "$HAS_METRICS" = "NO" ] && echo " ⚠️ Add quantifiable impact metrics (benchmarks, latency, test results)."
echo "Audit complete."

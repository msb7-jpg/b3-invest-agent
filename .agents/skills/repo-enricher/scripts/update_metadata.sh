#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Update GitHub Repo Metadata Non-Interactively
# Usage:
#   ./update_metadata.sh --desc "..." --topics "topic1,topic2,topic3" [--homepage "https://..."]
# ==============================================================================
set -euo pipefail

DESC=""
TOPICS=""
HOMEPAGE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--desc|--description)
            DESC="$2"
            shift 2
            ;;
        -t|--topics)
            TOPICS="$2"
            shift 2
            ;;
        -h|--homepage)
            HOMEPAGE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$DESC" ] && [ -z "$TOPICS" ] && [ -z "$HOMEPAGE" ]; then
    echo "Usage: $0 --desc \"Description\" --topics \"topic1,topic2\" [--homepage \"https://...\"]"
    exit 1
fi

CMD=(gh repo edit)

if [ -n "$DESC" ]; then
    CMD+=(--description "$DESC")
fi

if [ -n "$HOMEPAGE" ]; then
    CMD+=(--homepage "$HOMEPAGE")
fi

if [ -n "$TOPICS" ]; then
    CMD+=(--add-topic "$TOPICS")
fi

echo "Executing: ${CMD[*]}"
"${CMD[@]}"
echo "✅ GitHub repository metadata updated successfully."

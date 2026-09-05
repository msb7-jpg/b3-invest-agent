#!/usr/bin/env bash
# repo_info.sh - Agnostically extracts comprehensive GitHub repository info as JSON

set -euo pipefail

# Verify gh is installed
if ! command -v gh &> /dev/null; then
  echo '{"error": "gh cli is not installed or not in PATH"}' >&2
  exit 1
fi

# Verify git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
  echo '{"error": "Not inside a git repository"}' >&2
  exit 1
fi

# Gather agnostic repo metadata
gh repo view --json name,nameWithOwner,owner,description,homepageUrl,visibility,isPrivate,isFork,defaultBranchRef,repositoryTopics,parent,licenseInfo

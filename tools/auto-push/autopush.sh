#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
cd "$PROJECT_DIR"

# Sync latest from origin
# Rebase onto origin/main even if there are local unstaged/unstashed changes
# (stash automatically and re-apply)
git pull --rebase --autostash origin main

# Stage all changes (including untracked)
git add -A

# If nothing is staged, skip
if git diff --cached --quiet; then
  echo "No changes. Skipping commit."
  exit 0
fi

# Commit and push
git commit -m "auto: update via Codex ($(date '+%Y-%m-%d %H:%M'))"
git push origin main
echo "Pushed."

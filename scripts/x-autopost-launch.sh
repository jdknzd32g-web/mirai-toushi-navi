#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root
REPO_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$REPO_DIR"

echo "[x-autopost] repo: $REPO_DIR"

# Options
ROOT_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT_ARG="$2"; shift 2;;
    *) echo "[x-autopost] unknown arg: $1"; exit 1;;
  esac
done

# Ensure logs
mkdir -p "$REPO_DIR/logs"

# Install deps (idempotent)
if ! command -v npm >/dev/null 2>&1; then
  echo "[x-autopost] npm not found. Please install Node.js >= 18"
  exit 1
fi
echo "[x-autopost] installing deps (npm i)"
npm i >/dev/null 2>&1 || npm i

# Ensure .env
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "[x-autopost] Created .env from example. Please edit .env with your X API keys and rerun."
  exit 1
fi

# Auth check
echo "[x-autopost] checking X authentication"
if ! npx tsx src/check-auth.ts >/dev/null 2>&1; then
  echo "[x-autopost] Auth check failed. Run: npx tsx src/check-auth.ts で詳細を確認してください。"
  exit 1
fi

# Prepare crontab entries
CRON_TMP=$(mktemp)
crontab -l 2>/dev/null > "$CRON_TMP" || true

# Baseline env
SHELL_LINE="SHELL=/bin/zsh"
PATH_LINE="PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"
REPO_LINE="REPO=$REPO_DIR"
ROOT_DEF="${ROOT_ARG:-/Users/satoshioka/past_script}"
ROOT_LINE="ROOT=$ROOT_DEF"

ensure_line() {
  local line="$1"
  grep -Fq "$line" "$CRON_TMP" || echo "$line" >> "$CRON_TMP"
}

ensure_line "$SHELL_LINE"
ensure_line "$PATH_LINE"
ensure_line "$REPO_LINE"
ensure_line "$ROOT_LINE"

MORNING="30 7 * * * cd $REPO && npx tsx src/x-post.ts --slot morning --root \"$ROOT\" >> $REPO/logs/x-post.log 2>&1"
NOON="30 12 * * * cd $REPO && npx tsx src/x-post.ts --slot noon --root \"$ROOT\" >> $REPO/logs/x-post.log 2>&1"
EVENING="30 19 * * * cd $REPO && npx tsx src/x-post.ts --slot evening --root \"$ROOT\" >> $REPO/logs/x-post.log 2>&1"

ensure_line "$MORNING"
ensure_line "$NOON"
ensure_line "$EVENING"

crontab "$CRON_TMP"
rm -f "$CRON_TMP"

echo "[x-autopost] cron set for 07:30 / 12:30 / 19:30 (JST)"
echo "[x-autopost] root: $ROOT_DEF"
echo "[x-autopost] done. Logs: $REPO_DIR/logs/x-post.log"


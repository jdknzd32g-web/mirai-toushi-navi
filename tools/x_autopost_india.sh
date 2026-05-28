#!/bin/bash
# 2026-05-29 再投稿キュー: インド株を +4h で自動投稿する。
# 米国株バブル(post#1相当)は手動で即投稿済み。これは india(+4h) のみ。
# 画像は .webp（旧.png固定が原因で前回失敗したため修正済み）。
# 起動: nohup bash tools/x_autopost_india.sh >> tools/x_autopost.log 2>&1 &
set -u
cd /Users/satoshioka/mirai-toushi-navi
ENVPATH=/Users/satoshioka/youtube-project-share/.env
TSX=node_modules/.bin/tsx

post () {
  local draft="$1" image="$2"
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] posting: $draft"
  DOTENV_CONFIG_PATH="$ENVPATH" "$TSX" src/x-post-single.ts --draft "$draft" --image "$image" \
    2>&1 | grep -E "投稿完了|完了しました|ERROR|Error|✗|⚠|失敗"
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] done: $draft"
}

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] india queue start (sleep 4h -> india)"

sleep 14400   # +4h
post posts/drafts/9_india-stocks-next-decade.md blog/2026/india-stocks-next-decade/blog_india_stocks_header.webp

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] india queue finished"

#!/bin/bash
# 残り2本のXポストを4時間おきに自動投稿する常駐スクリプト。
# 1本目(資産防衛術)は手動で投稿済み。これは 2本目(+4h) と 3本目(+8h) を投げる。
# 起動: nohup bash tools/x_autopost_remaining.sh >> tools/x_autopost.log 2>&1 &
set -u
cd /Users/satoshioka/mirai-toushi-navi
ENVPATH=/Users/satoshioka/youtube-project-share/.env
TSX=node_modules/.bin/tsx

post () {
  local draft="$1" image="$2"
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] posting: $draft"
  DOTENV_CONFIG_PATH="$ENVPATH" "$TSX" src/x-post-single.ts --draft "$draft" --image "$image" \
    2>&1 | grep -E "投稿完了|完了しました|ERROR|Error|✗|失敗"
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] done: $draft"
}

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] queue start (sleep 4h -> post#2, sleep 4h -> post#3)"

sleep 14400   # +4h
post posts/drafts/8_us-stock-bubble-2026.md blog/2026/us-stock-bubble-2026/blog_us_stock_bubble_header.png

sleep 14400   # +8h
post posts/drafts/9_india-stocks-next-decade.md blog/2026/india-stocks-next-decade/blog_india_stocks_header.png

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] queue finished"

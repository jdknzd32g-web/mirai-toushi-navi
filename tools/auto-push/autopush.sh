#!/usr/bin/env bash
set -euo pipefail

# ⚠️ 自動push/pull（自動同期）は無効化しました。
# 今後は push / pull を手動で行う運用に切り替えています。
# （自動 rebase による同期エラーを防ぐため）
#
# 手動での同期は次のコマンドで行ってください:
#   git pull --rebase origin main    # 取り込み
#   git add -A && git commit -m "..." && git push origin main   # 反映
#
# もし自動pushを再び有効化したい場合は、このファイル末尾の
# 旧処理のコメントを外してください。

echo "自動同期は無効です（手動運用）。何も実行せず終了します。"
exit 0

# ---- 以下は旧・自動push処理（無効化済み。必要時のみ復活） ----
# PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
# cd "$PROJECT_DIR"
#
# # Sync latest from origin
# git pull --rebase --autostash origin main
#
# # Generate sitemap before committing
# echo "📝 Generating sitemap..."
# npx tsx scripts/generate-sitemap.ts
# echo "✓ Sitemap generated"
#
# # Stage all changes (including untracked)
# git add -A
#
# # If nothing is staged, skip
# if git diff --cached --quiet; then
#   echo "No changes. Skipping commit."
#   exit 0
# fi
#
# # Commit and push
# git commit -m "auto: update via Codex ($(date '+%Y-%m-%d %H:%M'))"
# git push origin main
# echo "Pushed."

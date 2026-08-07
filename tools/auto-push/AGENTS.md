# Codex Auto Push Agent（無効化済み）

⚠️ 自動push/pull（自動同期）は無効化しました。
今後は push / pull を手動で行う運用です（自動 rebase による同期エラーを防ぐため）。

## 手動での同期手順
- 取り込み: `git pull --rebase origin main`
- 反映: `git add -A` → `git commit -m "..."` → `git push origin main`

`autopush.sh` は呼び出されても何も実行せず終了します。
再び自動化したい場合は `autopush.sh` 末尾の旧処理コメントを外してください。

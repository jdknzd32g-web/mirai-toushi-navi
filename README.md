**ローカルcronでX自動投稿（1日3回）**

- 07:30 / 12:30 / 19:30（JST）に自動投稿
- 投稿前に `--dry-run` で検証可能
- コンテンツは `/Users/satoshioka/YouTube project` を優先、なければ `/Users/satoshioka/past_script`
- 対象拡張子: `.md` `.mdx` `.txt`

要件（実装済み）
- です・ます調、比喩と具体例でやさしく
- 1ポスト 130〜140字（理想: 139〜140字）
- 絵文字: 1センテンス1個、最大2個
- ハッシュタグ: 0〜2（例: `#新NISA #資産運用`）
- OAuth 1.0a User Context で投稿（App-only不可）
- 60日以内の意味類似は回避（簡易Jaccardで重複チェック）

セットアップ
1) 依存をインストール
```
npm i
```
2) 環境変数を設定
```
cp .env.example .env
# 値を記入:
# X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, X_BEARER_TOKEN
# CONTENT_ROOTS は任意（未設定なら既定パスを使用）
```

dry-run（検証）
```
npx tsx src/dry-run.ts --slot morning --root "/Users/satoshioka/YouTube project"
```

実投稿
```
npx tsx src/x-post.ts --slot morning --root "/Users/satoshioka/YouTube project"
```

cron設定（例）
```
crontab -e
# 以下を編集・貼り付け（Node/リポジトリパスを調整）
# 07:30 / 12:30 / 19:30 JST
30 7 * * *  cd /Users/satoshioka/Downloads/mirai-toushi-navi && npx tsx src/x-post.ts --slot morning --root "/Users/satoshioka/YouTube project" >> logs/x-post.log 2>&1
30 12 * * * cd /Users/satoshioka/Downloads/mirai-toushi-navi && npx tsx src/x-post.ts --slot noon    --root "/Users/satoshioka/YouTube project" >> logs/x-post.log 2>&1
30 19 * * * cd /Users/satoshioka/Downloads/mirai-toushi-navi && npx tsx src/x-post.ts --slot evening --root "/Users/satoshioka/YouTube project" >> logs/x-post.log 2>&1
```

ファイル構成
- `src/x-post.ts` 投稿本体（OAuth 1.0a User Context）
- `src/dry-run.ts` 事前検証（長さ・重複チェック・下書き出力）
- `src/lib/fs.ts` ルート探索・ファイル読込
- `src/lib/text.ts` 見出し・結論抽出、長さ判定
- `src/lib/style.ts` 文章生成（です・ます調、絵文字/ハッシュタグ調整）
- `src/lib/dedupe.ts` 簡易類似度（Jaccard）とシグネチャ
- `src/lib/queue.ts` 投稿履歴・キュー管理（`posts/.posted.json` / `posts/.queue.json`）
- `scripts/cron-templates.sh` crontabテンプレ

履歴とキュー
- `posts/.posted.json` に `{date, file, text, sig}` を追記
- `posts/.queue.json` は将来的なキュー投入用（現状は未使用の雛形）

エラーハンドリング
- 失敗時は `stderr` に1行で原因を出力

補足
- 「意味類似」の判定は簡易Jaccardのため完全一致ではありません。必要に応じてしきい値（`0.85`）を調整してください。
- 抽出精度は台本の構造に依存します。`結論/まとめ/要点/ポイント` 等の見出しがあると精度が上がります。


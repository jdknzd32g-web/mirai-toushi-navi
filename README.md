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

---

## ブログ記事自動生成システム

テキストファイルと画像ファイルを指定するだけで、ブログ記事（HTML）を自動生成し、
必要なファイル（category-region.html、blog/index.html、sitemap.xml）を自動更新します。

### 使い方

```bash
# 基本的な使い方
./scripts/auto-create-blog.sh ~/Desktop/テキストファイル.txt ~/Desktop/画像.jpg region4

# カテゴリーを指定する場合
./scripts/auto-create-blog.sh ~/Desktop/テキストファイル.txt ~/Desktop/画像.jpg nisa-guide11 nisa
```

### 引数

1. **テキストファイルのパス**（必須）: 記事本文のテキストファイル
   - 最初の `# ` で始まる行がタイトルになります
   - Markdownの基本的な記法（`##`、`###`、`**太字**`など）をサポート

2. **画像ファイルのパス**（必須）: OGP画像およびヘッダー画像
   - JPEG、PNG、GIF、WebP対応

3. **スラッグ**（必須）: 記事のID（URLやディレクトリ名に使用）
   - 例: `region4`、`nisa-guide11`

4. **カテゴリー**（オプション、デフォルト: `region`）
   - `region`: 地域別資産運用
   - `nisa`: 新NISA
   - `mutual-fund`: 投資信託

### 自動処理される内容

1. `blog/2025/{スラッグ}/` ディレクトリを作成
2. 画像を `{スラッグ}-image.{拡張子}` としてコピー
3. HTMLファイルを生成（SEO対応、OGP、Twitter Card、構造化データ付き）
4. `blog/category-{カテゴリー}.html` に新記事を追加
5. `blog/index.html` に新記事を追加
6. `sitemap.xml` を更新

### 直接TypeScriptスクリプトを実行する場合

```bash
npx tsx scripts/create-blog-post.ts \
  --text ~/Desktop/記事.txt \
  --image ~/Desktop/画像.jpg \
  --slug region4 \
  --category region
```

---

## X投稿画像対応

X（Twitter）投稿に画像を添付できるスクリプトを追加しました。

### 使い方

```bash
# 画像付きでX投稿（dry-run）
npx tsx src/x-post-with-image.ts \
  --file ~/Desktop/テキスト.txt \
  --image ~/Desktop/画像.jpg \
  --dry-run

# 実際に投稿
npx tsx src/x-post-with-image.ts \
  --file ~/Desktop/テキスト.txt \
  --image ~/Desktop/画像.jpg

# スロット指定で投稿
npx tsx src/x-post-with-image.ts \
  --slot morning \
  --root "/Users/satoshioka/YouTube project" \
  --image ~/Desktop/画像.jpg
```

### オプション

- `--file`: テキストファイルのパス
- `--image`: 画像ファイルのパス（JPEG、PNG、GIF、WebP対応）
- `--slot`: 投稿スロット（morning / noon / evening）
- `--root`: コンテンツルートディレクトリ
- `--dry-run`: 実際には投稿せず、確認のみ
- `--force`: 類似投稿チェックをスキップ

### ファイル構成

- `src/x-post-with-image.ts`: 画像対応版X投稿スクリプト
- `scripts/create-blog-post.ts`: ブログ記事自動生成スクリプト
- `scripts/auto-create-blog.sh`: ブログ記事作成用シェルスクリプト


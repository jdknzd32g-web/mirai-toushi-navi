# ブログ記事作成フロー（標準化版）

このドキュメントは、未来投資naviブログの新規記事を作成する際の標準フローです。

## 📋 事前準備

- [ ] 記事のテキストコンテンツを準備（デスクトップまたは指定フォルダ）
- [ ] ターゲットキーワードを明確化
- [ ] 記事カテゴリを決定（NISA、投資信託、地域別など）

---

## 🗂️ 1. フォルダ・ファイル作成

### 1-1. フォルダ構造の確認
```
blog/
└── 2025/
    ├── nisa-start-guide1/
    ├── region/
    │   └── [city-name]/
    └── [category]/
```

### 1-2. 新規フォルダ作成
- [ ] 適切なカテゴリフォルダ内に記事用フォルダを作成
- [ ] フォルダ名はURLフレンドリーな名前（例: `tosu-city`, `nisa-start-guide10`）

### 1-3. HTMLファイル作成
- [ ] `[folder-name].html` を作成（フォルダ名と同じ）
- [ ] 既存ブログの構造をテンプレートとして使用

---

## 🏷️ 2. メタデータ設定

### 2-1. 基本メタタグ
- [ ] `<title>`: 記事タイトル + "| 未来投資navi"
- [ ] `<meta name="description">`: 120〜160文字の説明文
- [ ] `<meta charset="UTF-8">`
- [ ] `<meta name="viewport">`: レスポンシブ対応
- [ ] `<link rel="canonical">`: 正規URL設定

**テンプレート:**
```html
<title>記事タイトル | 未来投資navi</title>
<meta name="description" content="記事の要約（120-160文字）">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="https://eva-solution.netlify.app/blog/2025/category/article-name/article-name.html">
```

### 2-2. OGP（Open Graph Protocol）タグ
- [ ] `og:type`: "article"
- [ ] `og:title`: 記事タイトル
- [ ] `og:description`: meta descriptionと同じ
- [ ] `og:url`: 記事の完全URL
- [ ] `og:image`: SNS共有用画像の完全URL
- [ ] `og:site_name`: "未来投資navi"
- [ ] `og:locale`: "ja_JP"

**テンプレート:**
```html
<meta property="og:type" content="article">
<meta property="og:title" content="記事タイトル">
<meta property="og:description" content="記事の要約">
<meta property="og:url" content="https://eva-solution.netlify.app/blog/2025/category/article-name/article-name.html">
<meta property="og:image" content="https://eva-solution.netlify.app/blog/2025/category/article-name/article-name-image.jpg">
<meta property="og:site_name" content="未来投資navi">
<meta property="og:locale" content="ja_JP">
```

### 2-3. Twitter Card タグ
- [ ] `twitter:card`: "summary_large_image"
- [ ] `twitter:title`: 記事タイトル
- [ ] `twitter:description`: meta descriptionと同じ
- [ ] `twitter:image`: SNS共有用画像の完全URL

**テンプレート:**
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="記事タイトル">
<meta name="twitter:description" content="記事の要約">
<meta name="twitter:image" content="https://eva-solution.netlify.app/blog/2025/category/article-name/article-name-image.jpg">
```

### 2-4. Article タグ
- [ ] `article:tag`: キーワードタグ（複数可）
- [ ] `article:published_time`: 公開日時（ISO 8601形式）
- [ ] `article:author`: 著者名

**テンプレート:**
```html
<meta property="article:tag" content="新NISA">
<meta property="article:tag" content="資産運用">
<meta property="article:published_time" content="2025-10-24T00:00:00+09:00">
<meta property="article:author" content="りょう">
```

---

## 🔗 3. 構造化データ（JSON-LD）

### 3-1. Article スキーマ
- [ ] `@type`: "Article"
- [ ] `headline`: 記事タイトル
- [ ] `description`: meta descriptionと同じ
- [ ] `image`: 画像URLの配列
- [ ] `datePublished`: 公開日時
- [ ] `dateModified`: 更新日時
- [ ] `author`: 著者情報（name, url）
- [ ] `publisher`: サイト情報（name, logo）

**テンプレート:**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "記事タイトル",
  "description": "記事の要約",
  "image": [
    "https://eva-solution.netlify.app/blog/2025/category/article-name/article-name-image.jpg"
  ],
  "datePublished": "2025-10-24T00:00:00+09:00",
  "dateModified": "2025-10-24T00:00:00+09:00",
  "author": {
    "@type": "Person",
    "name": "りょう",
    "url": "https://eva-solution.netlify.app/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "未来投資navi",
    "logo": {
      "@type": "ImageObject",
      "url": "https://eva-solution.netlify.app/images/logo.png"
    }
  }
}
```

### 3-2. BreadcrumbList スキーマ
- [ ] パンくずリストを構造化データとして記述
- [ ] トップ → カテゴリ → 記事 の階層

**テンプレート:**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "ホーム",
      "item": "https://eva-solution.netlify.app/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "ブログ",
      "item": "https://eva-solution.netlify.app/blog/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "記事タイトル",
      "item": "https://eva-solution.netlify.app/blog/2025/category/article-name/article-name.html"
    }
  ]
}
```

---

## 🎨 4. デザイン・スタイル設定

### 4-1. CSSリンク
- [ ] 共通スタイルシート: `/blog/css/blog-style.css`
- [ ] レスポンシブ対応確認

### 4-2. HTMLクラス・構造
- [ ] `.article-container`: メインコンテナ
- [ ] `.article-header`: ヘッダー画像エリア
- [ ] `.article-content`: 本文エリア
- [ ] `.highlight`: ハイライト表示
- [ ] `.number-box`: 数字強調ボックス
- [ ] `.calculation`: 計算例表示
- [ ] `.youtube-cta`: YouTube誘導CTA
- [ ] `.line-cta`: LINE誘導CTA

### 4-3. デザイン要素チェックリスト
- [ ] ヘッダー画像（1200x630px推奨）
- [ ] 見出し階層（h2 → h3 → h4）
- [ ] リスト表示（ul, ol）
- [ ] 強調表示（`<strong>`, `.highlight`）
- [ ] CTAボタン（YouTube, LINE）
- [ ] レスポンシブ表示確認

---

## 🔗 5. リンクチェック

### 5-1. 内部リンク
- [ ] トップページへのリンク: `/` または `/index.html`
- [ ] ブログ一覧ページ: `/blog/` または `/blog/index.html`
- [ ] 関連記事リンク: 正しい相対パスまたは絶対パス
- [ ] ロゴ画像リンク: `/images/logo.png`

**確認コマンド（grep）:**
```bash
grep -o 'href="[^"]*"' [file-name].html
```

### 5-2. 外部リンク
- [ ] YouTube チャンネル: `https://www.youtube.com/@investment_navi`
- [ ] LINE公式: `https://lin.ee/FxIOpk1`
- [ ] X（Twitter）シェアボタン: 正しいURL encoding
- [ ] すべて `target="_blank"` 設定

### 5-3. パンくずリスト
- [ ] ホーム → ブログ → 記事 の順
- [ ] 各リンクが正しく機能

---

## 🖼️ 6. SNS画像対応

### 6-1. 画像仕様
- [ ] ファイル名: `[article-name]-image.jpg`
- [ ] 推奨サイズ: 1200x630px（OGP標準）
- [ ] フォーマット: JPG または PNG
- [ ] ファイルサイズ: 500KB以下推奨

### 6-2. 画像配置
- [ ] 記事フォルダ内に配置
- [ ] OGPタグに完全URLで記載
- [ ] Twitter Card タグにも同じ画像URL

### 6-3. alt属性
- [ ] `<img>` タグには必ず `alt` 属性を設定
- [ ] 画像内容を簡潔に説明

---

## 📊 7. Google Analytics・タグ設定

### 7-1. Google Analytics
- [ ] GAタグが `<head>` 内に存在
- [ ] 測定ID: `G-XXXXXXXXXX`

**テンプレート:**
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 7-2. その他トラッキング
- [ ] 必要に応じてFacebook Pixel, X Pixelなど

---

## 🚀 8. デプロイ前チェック

### 8-1. バリデーション
- [ ] HTML構文エラーがないか（W3C Validator使用推奨）
- [ ] リンク切れがないか
- [ ] 画像の読み込み確認

### 8-2. プレビュー確認
- [ ] ローカルでHTMLをブラウザで開いて表示確認
- [ ] レスポンシブ表示確認（PC、タブレット、スマホ）
- [ ] 各リンクのクリック動作確認

### 8-3. SEOチェック
- [ ] タイトルは60文字以内
- [ ] meta descriptionは120〜160文字
- [ ] 見出しタグの階層が正しい
- [ ] 画像にalt属性が設定されている

---

## 📤 9. デプロイ

### 9-1. Git操作
```bash
# 変更をステージング
git add blog/2025/category/article-name/

# コミット
git commit -m "Add new blog post: [記事タイトル]"

# プッシュ
git push origin main
```

### 9-2. Netlify確認
- [ ] 自動ビルドが開始されたか確認
- [ ] ビルドが成功したか確認（約1〜3分）
- [ ] デプロイされたURLにアクセスして表示確認

### 9-3. 本番確認
- [ ] 記事が正しく表示されているか
- [ ] OGP画像が正しく表示されるか（Facebook Debugger, Twitter Card Validatorで確認）
- [ ] Google Analytics でアクセスが記録されるか

**OGP確認ツール:**
- Facebook: https://developers.facebook.com/tools/debug/
- Twitter: https://cards-dev.twitter.com/validator
- LinkedIn: https://www.linkedin.com/post-inspector/

---

## ✅ 10. 公開後対応

### 10-1. SNS投稿
- [ ] X（Twitter）で記事を告知
- [ ] LINE公式アカウントで配信（必要に応じて）
- [ ] YouTubeコミュニティ投稿（必要に応じて）

### 10-2. サイトマップ更新
- [ ] `sitemap.xml` に記事URLを追加（自動生成の場合は不要）
- [ ] Google Search Console で再送信

### 10-3. 内部リンク追加
- [ ] ブログ一覧ページに新記事を追加
- [ ] 関連記事がある場合、相互リンクを設定

---

## 📝 チェックリスト（簡易版）

記事作成時にこのリストを使って確認してください：

- [ ] フォルダ・ファイル作成完了
- [ ] メタタグ（title, description, canonical）設定
- [ ] OGPタグ設定（6つ以上）
- [ ] Twitter Cardタグ設定
- [ ] Article タグ設定
- [ ] JSON-LD構造化データ（Article + BreadcrumbList）
- [ ] 内部リンク確認（最低3箇所）
- [ ] 外部リンク確認（YouTube, LINE）
- [ ] 画像設定（OGP画像、alt属性）
- [ ] Google Analyticsタグ設定
- [ ] レスポンシブ表示確認
- [ ] Git commit & push
- [ ] Netlify ビルド確認
- [ ] 本番URL確認
- [ ] OGP表示確認（Facebook Debugger）
- [ ] SNS投稿完了

---

## 🔧 トラブルシューティング

### 問題: 画像が表示されない
**原因:** パスが間違っている、ファイル名が一致していない
**対処:**
- 絶対パスで記述（`https://eva-solution.netlify.app/...`）
- ファイル名の大文字小文字を確認
- ブラウザのデベロッパーツールでエラー確認

### 問題: OGP画像がSNSで表示されない
**原因:** キャッシュが残っている、URLが間違っている
**対処:**
- Facebook Debugger でキャッシュをクリア
- 画像URLが完全なhttps URLになっているか確認
- 画像サイズが1200x630pxになっているか確認

### 問題: リンクが404エラー
**原因:** 相対パスが間違っている、ファイルが存在しない
**対処:**
- 相対パスの階層を確認（`../../../` など）
- 絶対パス（`/blog/...`）で記述を検討
- ファイルが実際に存在するか確認

---

## 📚 参考ファイル

テンプレートとして参照できる既存ブログ記事：

1. **NISA記事:** `/blog/2025/nisa-start-guide10/nisa-start-guide10.html`
   - 標準的な記事構造
   - YouTube/LINE CTA設置例

2. **地域記事:** `/blog/2025/region/tosu-city/tosu-city.html`
   - 地域特化記事の構造
   - 地域タグの設定例

3. **ブログ一覧:** `/blog/index.html`
   - 記事リスト表示
   - カテゴリ分類

---

このフローに従うことで、SEO最適化された高品質なブログ記事を一貫性を持って作成できます。

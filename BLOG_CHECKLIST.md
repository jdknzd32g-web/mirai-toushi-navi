# ブログ記事投稿チェックリスト

このチェックリストは、mirai-toushi-naviプロジェクトで新しいブログ記事を投稿する際に確認すべき項目をまとめたものです。

## 1. ファイル準備

- [ ] テキストファイル（記事本文）を準備
- [ ] 画像ファイル（OGP/ヘッダー画像）を準備
- [ ] スラッグ（記事ID）を決定
- [ ] カテゴリーを決定（region / nisa / mutual-fund）

## 2. HTMLファイルのチェック

### 基本情報
- [ ] `<title>` タグが適切に設定されている
- [ ] `<meta name="description">` が適切に設定されている
- [ ] 日付が正しい（`<span class="date">`）

### OGP（Open Graph Protocol）設定
- [ ] `og:url` のパスが正しい
  - 例: `https://eva-solution.netlify.app/blog/2025/mutual-fund6/mutual-fund6.html`
- [ ] `og:title` が設定されている
- [ ] `og:description` が設定されている
- [ ] `og:image` のパスが正しい
  - 例: `https://eva-solution.netlify.app/blog/2025/mutual-fund6/mutual-fund-image6.jpg`
- [ ] `og:site_name` が "未来投資navi" になっている

### Twitter Card設定
- [ ] `twitter:card` が "summary_large_image" になっている
- [ ] `twitter:title` が設定されている
- [ ] `twitter:description` が設定されている
- [ ] `twitter:image` のパスが正しい（OGPと同じ画像）

### 内部リンク
- [ ] 「トップページへ戻る」のリンクが `../../../index.html` になっている
- [ ] YouTubeリンクが `https://www.youtube.com/@investment_navi` になっている
- [ ] LINEリンクが `https://lin.ee/FxIOpk1` になっている
- [ ] フッターの「メインページで詳細を見る」が `../../../index.html` になっている

### Google Analytics
- [ ] Google tag (gtag.js) が設定されている
- [ ] Tracking ID が `G-K4EG9Q6FL6` になっている

## 3. ファイル配置

- [ ] `blog/2025/{スラッグ}/` ディレクトリを作成
- [ ] HTMLファイルを `{スラッグ}.html` として保存
- [ ] 画像ファイルを適切な名前（例: `mutual-fund-image6.jpg`）で保存

## 4. カテゴリーページ更新（category-{カテゴリー}.html）

- [ ] 新しい記事を先頭に追加
- [ ] NEWバッジを新しい記事に付ける
- [ ] 古い記事からNEWバッジを削除
- [ ] 日付が正しい
- [ ] リンクパスが正しい（例: `2025/mutual-fund6/mutual-fund6.html`）
- [ ] 記事タイトルが正しい
- [ ] 記事の説明文が適切
- [ ] タグが適切に設定されている

## 5. ブログインデックス更新（blog/index.html）

- [ ] 該当カテゴリーのセクションに新記事を追加
- [ ] サムネイル画像のパスが正しい
- [ ] `alt` 属性が設定されている
- [ ] `loading="lazy" decoding="async"` が設定されている
- [ ] 記事タイトルが正しい
- [ ] 記事の説明文が適切

## 6. サイトマップ更新（sitemap.xml）

- [ ] 新しい記事のURLを追加
- [ ] `<lastmod>` に今日の日付を設定（例: 2025-10-27）
- [ ] `<changefreq>` を適切に設定（新記事は `weekly`）
- [ ] `<priority>` を適切に設定（新記事は `0.8`）
- [ ] `<image:image>` セクションを追加
  - [ ] `<image:loc>` に画像URLを設定
  - [ ] `<image:title>` に記事タイトルを設定

## 7. 最終確認

- [ ] すべてのファイルが適切な場所に配置されている
- [ ] 画像が表示される
- [ ] リンクが正しく機能する
- [ ] OGP画像が正しく表示される（SNSシェア確認ツールで確認）
- [ ] レスポンシブデザインが機能している

## 8. Git管理

- [ ] 変更をステージング
- [ ] コミットメッセージを記述
- [ ] リモートにプッシュ

## よくある間違い

### ❌ 間違い: パスに古いスラッグが残っている
```html
<meta property="og:url" content="https://eva-solution.netlify.app/blog/2025/investment-trust-guide/investment-trust-guide.html">
```

### ✅ 正解: 正しいスラッグを使用
```html
<meta property="og:url" content="https://eva-solution.netlify.app/blog/2025/mutual-fund6/mutual-fund6.html">
```

### ❌ 間違い: 画像ファイル名が統一されていない
```
investment-trust-guide-image.jpg
```

### ✅ 正解: カテゴリーとスラッグに合わせた命名
```
mutual-fund-image6.jpg
```

### ❌ 間違い: 相対パスが間違っている
```html
<a href="../../index.html" class="back-btn">トップページへ戻る</a>
```

### ✅ 正解: blog/2025/{スラッグ}/ からの正しい相対パス
```html
<a href="../../../index.html" class="back-btn">トップページへ戻る</a>
```

## スクリプトによる自動化

将来的には、以下のスクリプトを使用して作業を自動化することを推奨：

```bash
./scripts/auto-create-blog.sh ~/Desktop/テキストファイル.txt ~/Desktop/画像.jpg スラッグ カテゴリー
```

---

**更新日:** 2025-10-27
**バージョン:** 1.0

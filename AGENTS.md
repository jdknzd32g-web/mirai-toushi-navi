# 未来投資navi WEBサイト プロジェクト

## プロジェクト概要
50代・60代の投資初心者向けファイナンシャルプランニングサイト
- 運営：eva solution
- 目的：YouTube → 公式LINE → 個別相談 → FPコンサル契約への導線

## 重要ファイル（頻繁に更新）

### メインページ
- `/index.html` - トップページ（メインランディング）
- `/pricing.html` - 料金プランページ
- `/corporate-seminar.html` - 企業セミナー案内

### ブログ記事
- `/blog/2023/` - 2023年の記事一覧
- `/blog/mutual-fund1/mutual-fund1.html` - 投資信託記事1
- `/blog/mutual-fund2/mutual-fund2.html` - 投資信託記事2
- `/blog/mutual-fund3/mutual-fund3.html` - 投資信託記事3
- `/blog/mutual-fund4/mutual-fund4.html` - 投資信託記事4（candlestickチャート付き）

### NISAガイド記事
- `/blog/nisa-start-guide1/nisa-start-guide.html` - NISA入門ガイド1
- `/blog/nisa-start-guide2/nisa-start-guide2.html` - NISA入門ガイド2
- `/blog/nisa-start-guide3/nisa-start-guide3.html` - NISA入門ガイド3
- `/blog/nisa-start-guide4/nisa-start-guide4.html` - NISA入門ガイド4
- `/blog/nisa-start-guide5/nisa-start-guide5.html` - NISA入門ガイド5

### 地域別情報
- `/blog/region/region1.html` - 地域別投資情報

### カテゴリページ
- `/blog/category-mutual-fund.html` - 投資信託カテゴリ一覧
- `/blog/category-nisa.html` - NISAカテゴリ一覧
- `/blog/category-region.html` - 地域別カテゴリ一覧

## フォルダ構成

```
/WEBサイト
├── /blog/              # ブログコンテンツ
│   ├── /2023/         # 2023年記事アーカイブ
│   ├── /mutual-fund1-4/  # 投資信託解説記事（画像付き）
│   ├── /nisa-start-guide1-5/  # NISA入門ガイド（画像付き）
│   └── /region/       # 地域別投資情報
├── /images/           # サイト共通画像
│   ├── logo.png       # サイトロゴ
│   └── ryo-profile*.png  # プロフィール画像（3種類）
├── index.html         # トップページ
├── pricing.html       # 料金プラン
├── corporate-seminar.html  # 企業セミナー
├── simulation.html    # シミュレーション
├── robots.txt         # SEO設定
└── sitemap.xml       # サイトマップ
```

## 画像ファイル命名規則
- 記事内画像：`[記事名]-image[番号].jpg`
- プロフィール：`ryo-profile[番号].png`
- チャート：`candlestick-chart.jpg`

## 更新頻度の高いコンテンツ
1. **ブログ記事** - 週2-3回更新
2. **トップページ** - 最新記事の追加
3. **カテゴリページ** - 新記事追加時に更新

## コーディング規約
- 文字コード：UTF-8
- 改行コード：LF
- インデント：スペース2つ
- HTMLバージョン：HTML5
- 画像形式：JPEG（記事）、PNG（ロゴ・アイコン）

## エージェント起動時の挙動（自動解析オフ）
- このフォルダ（リポジトリ）を開いた直後は、自動でファイル一覧スキャン・全文検索・解析を行わない。
- `index.html` および `sitemap.xml` は、ユーザーからの明示的な指示がない限り読み込まない（初期表示・自動読み込みの対象外）。
- 初回は「待機状態」を保ち、必要な場合のみ簡潔に確認質問を行う。
- まとめての走査（例：`rg`/`grep` での全体検索、ディレクトリ横断の読み込み）は、実行前に同意を取る。
- ユーザーが具体的なファイルパスや更新内容を指示した場合のみ、対象ファイルを最小限で開く。
- 本方針は当リポジトリ配下の全作業に適用する。

## SEO関連ファイル
- `/robots.txt` - クローラー設定
- `/sitemap.xml` - サイトマップ（記事追加時に更新必要）
- `/google*.html` - Search Console認証ファイル

## よく使うコマンド例

### 新しいブログ記事を追加
```
新しいNISA記事を/blog/nisa-start-guide6/に作成して、
テンプレートはnisa-start-guide5を参考に
```

### カテゴリページの更新
```
category-nisa.htmlに新しい記事リンクを追加
```

### トップページの最新記事更新
```
index.htmlの最新記事セクションを更新して、
nisa-start-guide6を追加
```

## 注意事項
- 画像ファイルは必ず圧縮してからアップロード
- 新記事追加時はsitemap.xmlも更新
- モバイル表示の確認必須（50代・60代ユーザー考慮）
- 文字サイズは読みやすさ重視（16px以上推奨）

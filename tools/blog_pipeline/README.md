# 未来投資navi — 安全な記事制作フロー

## この版の範囲

本番非公開。公開済みHTML・LP・画像を変更せず、`dist/blog-preview/site` にだけサイトを構築する。
自動公開、コミット、push、外部への投稿機能は含めない。Vertex AIや新規有料APIは不要。
文章の生成・一次資料確認・Drive操作は、このタスクの毎朝9時の定期実行が担当する。
Pythonは固定テンプレートへの変換と検査だけを担当し、AIモデルを直接呼ばない。

## 保存場所と正本

- 公開用ソース：既存のリポジトリ。今回一切変更しない。
- 編集上の正本：Drive `mirai-toushi-navi`。IDは `editorial/drive-map.json`。
- Driveの `.json` 原稿：本文・メタ情報・出典を持つ構造化正本。内容を読み戻せるようMIMEはtext/plainで保存。
- Driveの `.md` 原稿：人が読むための同内容の出力。こちらに修正があれば、正本に反映してから再生成する。自動で踏みつぶさない。
- `editorial/articles/*.json`：Drive正本のローカル作業用キャッシュ。初回原稿もここにある。
- `editorial/existing-articles.json`：既存記事の検索用本文・見出し。既存HTMLから取得した読み取り専用の索引。
- Drive記事台帳：記事ID・タイトル・テーマ・検索意図・状態・予定URL・見出し。既存記事は「ローカルに存在、公開未照合」であり、本番公開済みと断定しない。
- `editorial/ryo-editorial-memory.md`：本人の方針と文体推定を分離。モデルの再学習ではない。
- `dist/blog-preview/`：ローカル専用プレビュー・画面検査結果。過去のプレビューはprevious-*へ退避して復旧可能。

`editorial/` と `dist/` はGitから除外し、通常の自動pushで原稿やローカルプレビューを公開しない。
Netlifyの公開ルートは現在 `.` なので、リポジトリ丸ごと手動アップロードは禁止。
DriveにもAPIキー・パスワード・顧客情報・ソースコード全体をアップロードしない。

## 実行

リポジトリ直下で実行する。

```sh
python3 tools/blog_pipeline/pipeline.py build
python3 -m unittest discover -s tools/blog_pipeline -p 'test_*.py' -v
python3 tools/blog_pipeline/serve.py
```

別のターミナルで：

```sh
node tools/blog_pipeline/visual-test.cjs
python3 tools/blog_pipeline/quality.py
```

確認画面： http://127.0.0.1:8765/review.html

サーバーはlocalhost限定。外部スクリプト・計測通信・埋め込みをCSPで遮断し、検索対象外を指定する。
Google Fontsも読み込まないため、実サイトとはフォントのフォールバックが異なる場合がある。
PlaywrightはPC同梱のランタイムと既存Google Chromeを使用する。OSによっては初回のブラウザー起動に許可が必要。
別の環境では `PLAYWRIGHT_PACKAGE` に利用するplaywright/package.jsonの絶対パスを指定する。

## 毎日の手順

1. `editorial/BUILD_IN_PROGRESS` があれば記事処理を止める。
2. Drive mapのIDで台帳・執筆方針・既存原稿を取得する。前回の更新時刻と照合する。
3. DriveまたはMarkdown閲覧版が更新されていれば内容を読み、構造化正本と照合する。競合・意図不明の場合は上書きせず報告する。
4. 同日のSBI1件＋その他1件が存在したら増やさない。未完の検査・同期だけ再開する。
5. 台帳のタイトル・見出しと検索用本文を比較する。検索意図・結論・具体例が同じ案は採用しない。文字列類似度は補助であり、意味の重複を保証するものではない。
6. 公式資料で事実確認。`editorial/articles/`の試作JSONに従い、原稿・具体例・FAQ・関連先・出典・確認日・重複確認理由を書く。
7. buildと単体テスト、表示検査を実行。`build-report.json`がstatic_pass、`visual-report.json`がpassでなければデザイン完了にしない。
8. 原稿・台帳・資料・方針・検証レポートをDriveへ同期する。既存ファイルはID維持のupdate_file、初回だけupload_file。書く直前にget_file_metadataでmodified_timeを再確認。更新があれば停止。text/plainまたはtext/markdownとして保存し、fetchで内容を読み返してローカルと照合する。
9. 成功後にdrive-mapのID・更新時刻・ローカルSHA256を保存する。同期失敗は未完としてログに残す。公開URLはあくまで予定、公開状態はdraftのまま。
10. りょうさんの承認前に本番ファイルを更新しない。毎回デザイン基準を作り直さない。

## デザイン保護

- ソースハッシュ：`editorial/source-lock.json`。LP・既存記事・画像・CSS・sitemapの変更や追加を検知したら停止。
- テンプレートハッシュ：`editorial/design-lock.json`。固定CSSや生成処理の変更を検知したら停止。
- 記事の入力は文字列をエスケープし、任意のHTML・CSSを原稿から実行させない。
- LPは既存の投資コラムsection一箇所だけ置換。存在しない／複数ある場合は停止。最新3件のみで追記し続けない。
- レイアウトCSSは記事ページ専用、LPの追加CSSは投資コラム区画内だけに適用。
- リンク先・画像・目次アンカー、H1数、ID重複、sitemapを検査。
- 表示検査は幅1440・768・390・320px。本文16px以上、画像切れ・横はみ出し・JS例外・HTTPエラーを確認。
- LPの記事欄以外の画像比較では、意図した記事欄の高さと固定オーバーレイを正規化。全体背景の高さ依存とスクロール位置による誤検出を分離する。色差1/255以内と、領域の0.005%以内の微小描画差のみ許容。領域の寸法差は別途検出する。
- これはローカルChromiumでの検証であり、全ブラウザーや本番外部サービスの表示を保証しない。
- 最終qualityゲートは、検査済みビルドのハッシュとDriveへ読み戻し確認したファイルのハッシュを照合する。再ビルド後は表示検査も再実行が必要。

## 既存データの注意

2026-09-13時点で既存記事86件を索引化。SBIのindex.htmlは記事本体なので含める。
元sitemap.xmlはXML記述エラーがあり、存在しない4ページのURLがあった。
プレビューのsitemapは存在確認済みのURLで再構築し、元ファイルは変更しない。
既存記事本文の全リンク修正や金融表現の全面監査は今回の範囲外。

## 承認後に行うこと（未実装・未実行）

公開用ファイルの差分確認、正式な公開日の設定、OGP・構造化データ・計測・本番リンクの確認、公開方法の確定を行う。
このプレビュー一式はnoindexと確認用ページを含むため、そのまま本番にコピーしない。
ユーザー承認後に公開用パッケージと公開後確認を追加する。自動公開の許可は別途必要。

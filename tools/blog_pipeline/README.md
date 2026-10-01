# 未来投資navi — 安全な記事制作フロー

## Evaの事業・セクション管理

このパイプラインはmirai-toushi-navi事業のブログセクション。YouTubeは同一事業、WAIZUは別事業。新規企画の前に`/Users/satoshioka/eva-solution-ops/00_strategy_management/business-sections.md`を読み、business-work-items.jsonへ事業・セクション・topic_id・intent・source_pathを登録し、`node tools/blog_pipeline/eva-governance.cjs check`を通す。同一事業の動画→記事はderived_fromで関連付ける。WAIZUの企画・素材・アカウントは混ぜず、既存の日次公開権限をWAIZUへ適用しない。

## 現行の公開権限（2026-09-13更新）

ユーザーが毎日の自動公開まで承認済み。`docs/daily-publishing.md`を現行手順とし、**日次2記事の作成・Drive同期・全検査合格→自動公開→本番検査合格→非SBI記事をX投稿**まで進める。以下の過去記録にある「公開には都度承認が必要」「日常の自動実行には組み込まない」はこの日次フローに限り上書きする。検査失敗時は公開・投稿しない。`RELEASE_DATE`で対象日を指定し、旧2バッチの固定コマンドを再利用しない。

## 本番公開済みの例外（2026-09-13）

最新の変更：ユーザー指示により、**本番公開・本番検査後の非SBI記事のX投稿のみ自動化済み**。`docs/x-after-deploy.md`に従う。`verify_release.cjs --production`は合格後に`post-published-x.cjs --send`を呼ぶ。15分ごとのフォローも未投稿を照合する。下記の「SNS投稿を自動化しない」はこの公開後処理には適用しない。毎朝の原稿作成だけで本番公開する権限は追加していない。

追記：追加2記事（SBI登録情報・家族向け資産一覧）も公開済み。合計4記事の公開記録は`editorial/published-releases.json`を優先する。追加公開パッケージは`dist/blog-release-additional/package.json`（5ファイル）。Git連携デプロイ・push前の統合は、下記初回パッケージに追加パッケージを重ねた最終状態を使用する。X投稿は今回明示承認された非SBIの2記事のみを`post-approved-x.cjs`で扱い、日常の自動実行には組み込まない。

ユーザーの明示指示により試作2記事をNetlify APIで公開済み。公開状態の正本記録は`editorial/published-releases.json`。下記の「未公開」は日常のプレビュー生成フローの説明であり、この2記事の本番状態には当てはまらない。台帳や原稿のdraft表記だけで再公開・再作成しない。

**本番とGitチェックアウトは未同期。次のGit連携デプロイ・push前に、`dist/blog-release/package.json`の7ファイルを確認・統合すること。** 現行の古いルートをそのままデプロイすると新記事が消える可能性がある。今回の本番公開は既存334ファイルのハッシュを引き継ぎ、2記事・共通CSS2件・LP・記事一覧・サイトマップだけを追加／更新した。既存LPと記事一覧の元デザインを保持し、私的な原稿・スクリプト・認証情報を追加アップロードしていない。

公開用生成は`package_release.py`、明示デプロイは`release.cjs`、配信確認は`verify_release.cjs`。これらは今回専用の対象ID固定ツールであり、日常の自動実行には組み込まない。次回は本番の最新ハッシュと公開済み状態を取得してから差分を作る。ローカルのプレビュー生成・検査が自動的に本番へ反映されることはない。Drive台帳の公開状態同期も別途必要。

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
node tools/blog_pipeline/design-check.cjs
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
7. buildと単体テスト、表示検査、`design-check.cjs`を実行。`build-report.json`がstatic_pass、`visual-report.json`と`design-report.json`がpassでなければ先に進まない。最後にquality.pyの合格を確認する。
8. 原稿・台帳・資料・方針・検証レポートをDriveへ同期する。通常は既存ファイルIDを維持してupdate_fileし、書く直前にget_file_metadataでmodified_timeを再確認する。更新・競合・安全レビューで既存更新が止まる場合は、りょうさん個人運用の正本管理として、対象フォルダへ `YYYY-MM-DD-NNN_用途_記事ID.ext` 形式の新規連番ファイルをupload_fileし、古い版は消さない。text/plainまたはtext/markdownとして保存し、fetchで内容を読み返してローカルと照合する。
9. 成功後にdrive-mapのID・更新時刻・ローカルSHA256・連番名を保存する。同期失敗は未完としてログに残す。公開URLはあくまで予定、公開状態はdraftのまま。正本の混乱は連番とdrive-mapの最新版参照で制御し、同日の再開時は最新連番を優先する。
10. りょうさんの承認前に本番ファイルを更新しない。毎回デザイン基準を作り直さない。

## 2026-10-02以降の原稿品質（必須）

制作前に `docs/blog-editorial-policy.md` と `editorial/ryo-voice-guide.md` を読む。新規原稿は `design.policy_version=2` を持ち、本文内の例え・具体例・行動と、直近7記事の図解・写真レビューを `editorial_quality` に保存する。`editorial_policy.py` がビルド時に検査し、不足・本文不一致・同じ構図の無説明な反復を停止する。構図はallocation/timeline/document/decision/flow/recordから意味に合わせて選ぶ。各部品のラベル・時期・書類名・判断結果は原稿データに指定する。旧原稿のcardsレイアウトは互換用で、新規記事には使わない。

既存の毎朝7時の定期実行はこのREADMEとdaily-publishing.mdを読むため、更新は次の実行から有効。検査合格のために既存の図解を変えたり、次の日の記事を先に生成したりしない。

## デザイン保護

2026-09-13承認：銅価格の記事を主基準とする。仕様は`docs/blog-design-spec.md`。
`design-check.cjs`は原本のハッシュを固定して、実ブラウザーで色・幅・見出し・ヘッダー順序・公式URL・YouTube・LINE・著者・まとめ・図解の有無とスマホの可読性を検査する。元記事の小さい補助文字はそのまま複製せず16px以上、図解はスマホで縦積みにする。
故障注入12件を毎回実行し、URL改変・部品削除・色や幅の変化・ヘッダー順序・小さい図解文字・非表示・横はみ出し・赤い強調・長文強調・関連記事装飾の消失を拒否する。すべてブラウザー内だけの変更で、原本を書き換えない。
最終ゲートはデザイン検査とビルドの指紋、検査ツール自身のハッシュを照合する。検査結果が古ければ停止する。テスト合格は公開許可ではない。

新規原稿JSONには`design.summary`（文字列配列）と`design.diagrams`を含める。節番号をキーに、構図・関係・選択理由・表示データを指定する。型ごとの項目と組数は`docs/blog-editorial-policy.md`に従う。すべてプレーンテキストとしてエスケープする。試作2記事のみ`design-content.json`をローカル補足として使用し、Drive原稿は勝手に上書きしない。補足は次回の承認済み同期で原稿へ統合する。図解やまとめのない原稿は生成を止める。

太字・ハイライトは設計書第11節に従う。`design.emphasis`に場所をキーとして`{"kind":"bold"または"highlight","text":"原文中の短い文字列"}`を設定する。対応キーは`lead.0`、`sections.1.paragraphs.0`、`summary.0`（節番号のみ1始まり、配列番号は0始まり）。段落内で一意に一致する40字以内の箇所だけを装飾し、曖昧・不一致・未対応の場所なら停止する。自由なHTMLは使わない。強調数・密度・色・禁止箇所・関連カードと出典リンクの装飾もブラウザー検査の対象。

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

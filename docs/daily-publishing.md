# 毎日の自動公開（2026-09-13承認）

## 実行スケジュール（2026-09-13変更）

- `automation-3`「毎日のフォローアップ・ブログ2記事公開」に統合。毎日9時（Asia/Tokyo）、ローカルの本プロジェクトで独立した新しい作業チャットとして実行する。
- 従来のメール・カレンダーフォローアップは平日のみ維持。ブログは土日も実施し、日曜日の休息案内も維持する。
- 旧15分間隔の `sbi-nisa-1` は停止（PAUSED）。昼・夕方の追加実行や15分監視は作成しない。
- 会話履歴ではなく記事台帳・公開記録・X送信記録・editorial-logから未完工程を引き継ぐ。過去日の案件は元の日付を保ち、まとめて不足記事を生成しない。競合や結果不明の送信は停止して報告する。
- メール・予定は確認と報告のみ。記事や公開データへ転用しない。WAIZU・YouTubeの制作や公開は対象外。

日次処理は日本時間9時以降に1回。SBI記事1件・非SBI記事1件を作成し、Drive同期・内容検査・デザイン検査がすべて成功したら、追加承認なしでブログ公開、本番検査、非SBI記事のX投稿まで進める。失敗時は停止して報告する。9月13日は4記事とも公開済みなので追加作成・再公開しない。

## 公開手順

各コマンドに同じ`RELEASE_DATE=YYYY-MM-DD`（対象原稿の日付）を付ける。出力は`dist/blog-release-YYYY-MM-DD`。以下は必ず順に実施する。

1. READMEの原稿作成・一次情報確認・重複チェック・Drive同期・単体テスト・デザイン・表示検査を完了し、`quality.py`が合格すること。重複チェックでは、記事JSONの`duplicate_review`で既存記事との差分を明記し、さらに`pipeline.py build`のタイトル類似・本文類似ゲートを必ず通す。類似判定で停止した場合は、同じテーマを言い換えて公開せず、別テーマへ差し替える。Drive同期は、各管理フォルダ配下の`YYYY-MM-DD`日付フォルダへ保存する。既存ファイル更新を基本とし、更新が安全レビュー・競合・所有者確認で止まる場合は、りょうさん個人運用の正本管理として新規連番ファイルへ同期し、読み戻し確認済みIDをdrive-mapの最新版として扱う。
2. `node tools/blog_pipeline/release.cjs inspect`：現在の本番を取得。ローカル公開ソースは過去のパッケージも含め、本番SHA1が一致したものだけ使用。
3. `python3 tools/blog_pipeline/package_release.py`：当日2記事のみ梱包。SBI/非SBI各1件を要求。既存記事の上書き禁止。共通CSSは同一なら再利用、変更されていれば停止。LPは既存枠の最新3件だけ差し替える。
4. `node tools/blog_pipeline/release.cjs draft`：既存本番マニフェストに対象ファイルだけ追加する。保存済みdeploy.jsonがあれば再作成せず状態を確認。
5. `node tools/blog_pipeline/release.cjs status`：readyを待つ。エラー・不明状態では公開しない。
6. `node tools/blog_pipeline/verify_release.cjs`：本番前の表示・リンク検査。追加で`PREVIEW_URL=<draft URL> node tools/blog_pipeline/design-check.cjs`を実行し、共通デザインも合格させる。
7. `node tools/blog_pipeline/release.cjs publish`：本番の直前状態が変わっていない場合だけ公開。公開ID照合後、published-releases.jsonを記録。
8. `node tools/blog_pipeline/verify_release.cjs --production`：本番を検査。合格後に非SBI記事のX投稿が自動実行される。失敗は公開失敗と投稿失敗を区別して報告する。
9. 既存リモートファイルが保持され、パッケージ外のハッシュ変更がないことを確認。Drive台帳へ公開URLと公開状態を同期・読み戻し、公開・X結果をeditorial-log.mdに記録。

## 中断・再開

作成済み記事、パッケージ、deploy.json、published記録、X送信記録を先に読み、未完の工程のみ再開する。本番が自分のdeploy.idなら再公開せず本番検証へ進む。第三者の本番更新があれば停止し、新しい本番からの再梱包が必要。同一エラーの自動反復、確認なしの再送をしない。

認証情報を公開パッケージへ含めない。Git push・フォルダ移動・YouTube側の改変・デザイン基準の緩和・新規有料サービス追加は日次処理に含めない。本番とGitチェックアウトの未同期は継続しているので、リポジトリ丸ごとデプロイは禁止。

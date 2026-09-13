# Eva事業統括の実装記録

- 事業帰属の正本：eva-solution-ops/00_strategy_management/business-registry.json
- 未来投資navi事業：YouTube・ブログ・X・LINE・相談。WAIZU：動画・音楽・ブランドの別事業。
- 共通企画台帳：business-work-items.json。新規案件用の空台帳を作成。既存全案件の移行は未実施。
- 同一事業の媒体展開：topic_idとderived_from。事業間の編集参考：reference_id。
- WAIZU→サムライトレードは編集参考関係のみ登録。参照URL・フォルダはユーザー確認待ち。
- Eva、YouTube、WAIZUのAGENTS.mdとブログ運用READMEに事業の照合・企画登録・検査手順を接続。
- eva-governance.cjs：パスの最長一致・実体パス解決、台帳の事業／セクション／親企画／参考関係検査。
- 10項目の検査が合格。既存X投稿テスト5項目も合格。
- 既存ファイルの移動・デプロイ・投稿・全案件取り込み・公開権限拡張は未実施。
- 運用ルールと補助CLIによる管理であり、OS隔離や全スクリプトの強制制御ではない。

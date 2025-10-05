起動時の自動解析を無効化する仕組み（AGENTS.md + .codex-noauto）:
- AGENTS.md に自動解析オフ方針を明記
- .codex-noauto で NO_AUTO_ANALYSIS=1 を設定
- EXCLUDE_ON_START=index.html,sitemap.xml を初期読み込みから除外
- 初回は待機し、走査は同意取得後のみ実行

# Git同期の保護

- 本番は検証済みの日次API公開を正とする。Gitはソース履歴の保存先。
- 旧autopush.shとauto_push.shは停止用の入口として残す。実行しても変更・送信しない。
- 自動rebase、autostash、一括add、旧sitemap生成を復活させない。
- Git同期はユーザーが依頼した範囲で変更を確認し、既存履歴を残す通常mergeで行う。force pushは禁止。
- push前にNetlifyのstop_builds=trueを確認し、source-lockの個別照合と検査を完了する。
- 詳細はdocs/daily-publishing.mdの「Git同期とAPI公開の分離」を読む。

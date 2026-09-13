# 2記事の公開記録 — 2026-09-13

公開先：eva-solution.com。Netlifyの既存サイトへ公開済み。

- [SBI証券の初回積立確認](https://eva-solution.com/blog/sbi-securities/first-order-checklist.html)
- [生活費・予備資金の家計メモ](https://eva-solution.com/blog/life-planning/cash-reserve-worksheet.html)

確認用表示とnoindexを外し、公開日・OGP・Article構造化データを追加。共通HTML構造、CSS、LINE、YouTube、図解、太字・ハイライトは承認済みのものを使用。

変更対象は2記事、共通CSS2件、LPの記事枠、既存記事一覧へのカード追加、サイトマップの7ファイル。元の記事一覧のCSSと既存カードは維持。サイトマップは未エスケープのアンパサンドを修復し、既存エントリを残して2記事を追加した。

## 検証

- Netlify確認用URLでデザイン検査：4画面幅、故障注入12件、合格。
- 本番URLで公開後確認：1440／390／320pxの2記事・LP・記事一覧、合格。
- canonical、OGP、構造化データ、検索除外解除、画像・CSS・記事リンク、サイトマップ掲載を確認。
- 本番ファイル数334→338。既存ファイル消失0、対象外のハッシュ変更0、送信内容不一致0。

Netlify公開ID：`6aa61fa7940d502be92622ea`。直前の公開ID：`6a8790380451af0008ac286c`。問題時はNetlifyの直前デプロイへ戻せる。

生成物と検査記録は`dist/blog-release/`。公開状態は`editorial/published-releases.json`に記録。

## 次回更新前の注意

今回の公開はNetlifyへの直接反映。Gitチェックアウトの公開用ルートとDrive台帳は未同期。古いルートからGit連携デプロイすると今回の追加分が失われるため、次のpush／Git連携デプロイ前に公開パッケージ7ファイルの取り込みと台帳同期を行う。日常の自動生成は従来どおりローカル限定で、自動再公開は行わない。

利用したデプロイ方式：[Netlify公式APIガイド](https://docs.netlify.com/api-and-cli-guides/api-guides/get-started-with-api/)。本番全ファイルのダイジェストを保持した確認用デプロイを作り、配信確認後に本番へ切り替えた。

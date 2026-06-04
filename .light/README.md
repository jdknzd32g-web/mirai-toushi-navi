# ライト（light）— 未来投資navi ブログ／SNS部門長

`mirai-toushi-navi`（ブログ）と X(SNS) 告知を担当する Claude Code サブエージェント。動画制作ワークフローの **経路②（1人語り台本 → ブログ → X告知）** を一手に引き受ける。ゆうちゃん（動画部門長）と対になる存在。

## 構成

```
~/.claude/agents/light.md                # ペルソナ定義（サブエージェント本体・マシンローカル）
mirai-toushi-navi/
├── .claude/commands/light.md            # /light スラッシュコマンド
└── .light/
    ├── README.md                        # このファイル
    └── light.md                         # ペルソナ実体（リポジトリ共有用のコピー）
```

> ⚠️ `~/.claude/agents/` はマシンローカルで git 同期されない。新しいマシンで使う時は `.light/light.md` の内容を `~/.claude/agents/light.md` にコピーすること（ゆうちゃんで実体が片方のマシンに無く欠落した事例があるため）。

## 呼び出し方

### A. `/light` スラッシュコマンド（推奨）
```
/light S&P500の1人語り台本をブログ化して公開して
/light この記事のSEOタイトルを3案出して
```

### B. メインセッションで自然文
「ライト、〜」と話しかける → メインの Claude が `Agent`（`subagent_type: "light"`）で起動。

## ナレッジ（執筆ルール）
- `BLOG_WRITING_MANUAL.md` … ペルソナ・基本方針・禁止事項
- `BLOG_CREATION_WORKFLOW.md` … 記事作成フロー
- `BLOG_CHECKLIST.md` / `BLOG_SCRIPT_TEMPLATE.md` / `AGENTS.md`

## 関連
- 動画制作ワークフロー（経路①②）：`youtube-project-share/obsidian/20_Scripts/マニュアル/ワークフロー/未来投資navi動画制作ワークフロー.md`
- 動画部門長：ゆうちゃん（`youtube-project-share/.yu-chan/`）

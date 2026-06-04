#!/usr/bin/env python3
# ブログ一覧ハブ blog/index.html を、実在する記事ファイルから機械生成する。
# リンクは実ファイルパスから作るので原理的にリンク切れが出ない。生成後に存在検証も行う。
import re, pathlib, sys, html as _html

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
BASE = "https://eva-solution.com"

# カテゴリ正規化（表示順）。キーワードで (なし) を推定。
BUCKETS = [
    ("新NISA",          ["nisa", "新nisa"]),
    ("米国株・指数",    ["s&p", "sp500", "sp-500", "fang", "米国", "us-stock", "us_stock", "index-vs", "インデックス vs", "個別株"]),
    ("投資信託・オルカン", ["投資信託", "mutual", "fund", "オルカン", "投信", "全世界"]),
    ("債券・資産防衛",   ["債券", "bond", "防衛", "守り", "ほったらかし"]),
    ("ゴールド・コモディティ", ["gold", "ゴールド", "silver", "シルバー", "貴金属", "コモディティ", "金投資"]),
    ("地域・新興国株",   ["インド", "india", "新興国", "region", "地域", "日本株", "japan", "サムライ"]),
    ("年金・ライフプラン", ["年金", "pension", "ライフプラン", "老後", "idec", "ideco"]),
    ("証券口座・制度",   ["証券", "sbi", "楽天", "口座", "securities", "経済圏"]),
]
DEFAULT_BUCKET = "資産運用"
ORDER = [b[0] for b in BUCKETS] + [DEFAULT_BUCKET]

def detect(title, cat, path):
    hay = f"{title} {path}".lower()
    # 明示カテゴリを優先的にバケットへ寄せる
    src = f"{cat} {hay}".lower()
    for name, kws in BUCKETS:
        for kw in kws:
            if kw in src:
                return name
    return DEFAULT_BUCKET

def collect():
    arts = []
    for p in sorted(BLOG.glob("**/*.html")):
        if p.name == "index.html":
            continue
        h = p.read_text(encoding="utf-8", errors="ignore")
        t = re.search(r"<title>(.*?)</title>", h, re.S)
        title = re.sub(r"\s+", " ", t.group(1)).strip() if t else p.stem
        title = title.split("｜")[0].split("|")[0].split("【")[0].strip() or p.stem
        # 元タイトル（装飾含む）も表示用に保持
        disp = re.sub(r"\s+", " ", t.group(1)).strip().split("｜")[0].split("|")[0].strip() if t else p.stem
        c = (re.search(r'article:section"\s+content="(.*?)"', h) or
             re.search(r'class="article-category">(.*?)<', h) or
             re.search(r'class="blog-tag">(.*?)<', h))
        cat = c.group(1).strip() if c else ""
        d = re.search(r'article:published_time"\s+content="(.*?)"', h)
        date = d.group(1).strip()[:10] if d else ""
        rel = p.relative_to(BLOG).as_posix()
        bucket = detect(title, cat, rel)
        arts.append({"rel": rel, "title": disp, "date": date, "bucket": bucket})
    return arts

def render(arts):
    groups = {}
    for a in arts:
        groups.setdefault(a["bucket"], []).append(a)
    for g in groups.values():
        g.sort(key=lambda x: x["date"], reverse=True)
    total = len(arts)
    sections = []
    for name in ORDER:
        if name not in groups:
            continue
        items = groups[name]
        lis = []
        for a in items:
            dt = a["date"] or ""
            lis.append(
                f'        <li><a href="{a["rel"]}"><span class="bi-title">{_html.escape(a["title"])}</span>'
                f'<span class="bi-date">{dt}</span></a></li>'
            )
        sections.append(
            f'    <section class="bi-cat">\n'
            f'      <h2>{_html.escape(name)} <span class="bi-count">{len(items)}</span></h2>\n'
            f'      <ul class="bi-list">\n' + "\n".join(lis) + "\n      </ul>\n    </section>"
        )
    body = "\n".join(sections)
    return TEMPLATE.format(total=total, body=body, base=BASE)

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ブログ記事一覧 | 未来投資navi</title>
  <meta name="description" content="未来投資naviのブログ記事一覧。新NISA・オルカン・米国株・債券・年金など、50代60代の投資初心者に向けた資産運用の記事をカテゴリ別にまとめています。">
  <link rel="canonical" href="{base}/blog/index.html">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{base}/blog/index.html">
  <meta property="og:title" content="ブログ記事一覧 | 未来投資navi">
  <meta property="og:description" content="50代60代の投資初心者に向けた資産運用の記事をカテゴリ別にまとめています。">
  <meta property="og:site_name" content="未来投資navi">
  <script type="application/ld+json">
  {{ "@context":"https://schema.org","@type":"CollectionPage","name":"ブログ記事一覧 | 未来投資navi","url":"{base}/blog/index.html" }}
  </script>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Hiragino Kaku Gothic ProN','Hiragino Sans','Noto Sans JP',sans-serif;font-size:16px;line-height:1.8;color:#333;background:#f9f9f7}}
    .container{{max-width:760px;margin:0 auto;padding:40px 24px 80px}}
    .bi-head{{margin-bottom:36px}}
    .bi-head .home{{display:inline-block;font-size:13px;color:#1a3a5c;text-decoration:none;margin-bottom:14px}}
    .bi-head .home:hover{{text-decoration:underline}}
    .bi-head h1{{font-size:26px;color:#1a1a1a;margin-bottom:8px}}
    .bi-head p{{font-size:14px;color:#888}}
    .bi-cat{{margin-bottom:40px}}
    .bi-cat h2{{font-size:18px;color:#1a3a5c;border-bottom:2px solid #1a3a5c;padding-bottom:8px;margin-bottom:14px}}
    .bi-count{{font-size:13px;color:#fff;background:#1a3a5c;border-radius:10px;padding:1px 9px;margin-left:6px;vertical-align:middle}}
    .bi-list{{list-style:none}}
    .bi-list li{{border-bottom:1px solid #ececec}}
    .bi-list a{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;padding:12px 4px;text-decoration:none;color:#2a3a4a;transition:background .15s}}
    .bi-list a:hover{{background:#f3f6fa}}
    .bi-title{{flex:1}}
    .bi-list a:hover .bi-title{{color:#1a3a5c;text-decoration:underline}}
    .bi-date{{flex-shrink:0;font-size:12px;color:#aaa;font-variant-numeric:tabular-nums}}
    @media(max-width:600px){{.bi-head h1{{font-size:21px}}.bi-list a{{flex-direction:column;gap:2px}}.bi-date{{font-size:11px}}}}
  </style>
</head>
<body>
  <div class="container">
    <header class="bi-head">
      <a class="home" href="../index.html">← トップページへ戻る</a>
      <h1>ブログ記事一覧</h1>
      <p>50代・60代の投資初心者に向けた資産運用の記事を、カテゴリ別にまとめています（全{total}記事）。</p>
    </header>
{body}
  </div>
</body>
</html>
"""

def main():
    arts = collect()
    out = BLOG / "index.html"
    out.write_text(render(arts), encoding="utf-8")
    print(f"wrote {out} ({len(arts)} articles)")
    # 存在検証
    missing = [a["rel"] for a in arts if not (BLOG / a["rel"]).exists()]
    print("リンク切れ:", len(missing))
    for m in missing:
        print("  MISSING:", m)
    return 0 if not missing else 1

if __name__ == "__main__":
    sys.exit(main())

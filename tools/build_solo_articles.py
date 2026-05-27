# -*- coding: utf-8 -*-
"""
99_Archive/1人語り の台本3本を blog/2026/ 形式の記事HTMLへ変換するワンショットビルダー。
- 既存の最高品質テンプレ index-vs-individual-stock.html から <style> と YouTubeバナー を流用
- 見出しSVGは自作（APIキー不要）
- ヘッダー写真は既存pngを仮置き（要差し替え）。プロフィール画像も配置。
- sitemap.xml に3件追記
"""
import re, shutil, datetime
from pathlib import Path

ROOT = Path("/Users/satoshioka/mirai-toushi-navi")
TPL = ROOT / "blog/2026/index-vs-individual-stock/index-vs-individual-stock.html"
DATE_ISO = "2026-05-27"
DATE_JP = "2026年5月27日"
BASE = "https://eva-solution.netlify.app"
YT = "https://www.youtube.com/channel/UCb-u1hcuQyo7qruBhuiOBZg"
LINE = "https://lin.ee/FxIOpk1"

tpl = TPL.read_text(encoding="utf-8")
STYLE = re.search(r"<style>.*?</style>", tpl, re.DOTALL).group(0)
YT_BANNER = re.search(r"(<a class=\"youtube-channel-banner\".*?</a>)", tpl, re.DOTALL).group(1)

PROFILE_SRC = TPL.parent / "blog_profile_ryo.jpg"
HERO_SRC = TPL.parent / "blog_index_vs_individual_stock_header.png"  # 仮置き用

GA = """    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-K4EG9Q6FL6"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        gtag('js', new Date());
        gtag('config', 'G-K4EG9Q6FL6');
    </script>"""

def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

def head(title, desc, keywords, slug, section, hero_name, jsonld_blocks):
    url = f"{BASE}/blog/2026/{slug}/{slug}.html"
    img = f"{BASE}/blog/2026/{slug}/{hero_name}"
    jl = "\n".join(jsonld_blocks)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
{GA}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="keywords" content="{esc(keywords)}">
  <link rel="canonical" href="{url}">

  <!-- OGP -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="675">
  <meta property="og:image:alt" content="{esc(title)}">
  <meta property="og:site_name" content="未来投資navi">
  <meta property="article:published_time" content="{DATE_ISO}">
  <meta property="article:author" content="りょう">
  <meta property="article:section" content="{esc(section)}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@investment_navi">
  <meta name="twitter:creator" content="@investment_navi">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{img}">
  <meta name="twitter:image:alt" content="{esc(title)}">

  <!-- 構造化データ -->
{jl}
{STYLE}
</head>"""

def jsonld_article(title, desc, slug, hero_name):
    url = f"{BASE}/blog/2026/{slug}/{slug}.html"
    img = f"{BASE}/blog/2026/{slug}/{hero_name}"
    t = esc(title); d = esc(desc)
    return f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{t}",
    "description": "{d}",
    "image": "{img}",
    "author": {{ "@type": "Person", "name": "りょう" }},
    "publisher": {{
      "@type": "Organization",
      "name": "未来投資navi",
      "logo": {{ "@type": "ImageObject", "url": "{BASE}/images/logo.png" }}
    }},
    "datePublished": "{DATE_ISO}",
    "dateModified": "{DATE_ISO}",
    "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{url}" }}
  }}
  </script>"""

def jsonld_breadcrumb(title, slug):
    url = f"{BASE}/blog/2026/{slug}/{slug}.html"
    return f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "ホーム", "item": "{BASE}/" }},
      {{ "@type": "ListItem", "position": 2, "name": "ブログ", "item": "{BASE}/blog/" }},
      {{ "@type": "ListItem", "position": 3, "name": "{esc(title)}", "item": "{url}" }}
    ]
  }}
  </script>"""

def jsonld_faq(qa):
    items = []
    for q, a in qa:
        items.append(f"""      {{ "@type": "Question", "name": "{esc(q)}", "acceptedAnswer": {{ "@type": "Answer", "text": "{esc(a)}" }} }}""")
    body = ",\n".join(items)
    return f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{body}
    ]
  }}
  </script>"""

def svg_panel(title, rows, c1, c2, accent="#f5c842", rowfill="#1e3f6a", rowstroke="#4a8abf", subcol="#a8c8e0"):
    """gradient bg + center title + stacked rows. rows=[(bold, sub)]"""
    gid = "g" + str(abs(hash((title, c1, c2))) % 100000)
    n = len(rows)
    parts = [
        f'<svg viewBox="0 0 720 405" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(title)}">',
        f'<defs><linearGradient id="{gid}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" style="stop-color:{c1}"/><stop offset="100%" style="stop-color:{c2}"/></linearGradient></defs>',
        f'<rect width="720" height="405" fill="url(#{gid})"/>',
        f'<text x="360" y="74" font-family="\'Hiragino Kaku Gothic ProN\',\'Hiragino Sans\',sans-serif" font-size="20" font-weight="bold" fill="#eef4fb" text-anchor="middle">{esc(title)}</text>',
    ]
    if n:
        box_h = 56; gap = 14; total = n * box_h + (n - 1) * gap
        y0 = 200 - total // 2 + 18
        for i, (b, s) in enumerate(rows):
            y = y0 + i * (box_h + gap)
            parts.append(f'<rect x="120" y="{y}" width="480" height="{box_h}" rx="8" fill="{rowfill}" stroke="{rowstroke}" stroke-width="1.5"/>')
            parts.append(f'<text x="360" y="{y+24}" font-family="\'Hiragino Kaku Gothic ProN\',\'Hiragino Sans\',sans-serif" font-size="16" fill="{accent}" text-anchor="middle" font-weight="bold">{esc(b)}</text>')
            if s:
                parts.append(f'<text x="360" y="{y+44}" font-family="\'Hiragino Kaku Gothic ProN\',\'Hiragino Sans\',sans-serif" font-size="12.5" fill="{subcol}" text-anchor="middle">{esc(s)}</text>')
    parts.append("</svg>")
    return '<div class="section-visual">' + "".join(parts) + "</div>"

def cta_box(heading, body):
    return f"""      <div class="cta-box">
        <h3>{heading}</h3>
        <p>{body}</p>
        <a href="{LINE}" target="_blank" rel="noopener noreferrer" class="cta-button">公式LINEで無料相談する</a>
      </div>"""

AUTHOR = f"""    <div class="author-box">
      <img class="author-photo" src="./blog_profile_ryo.jpg" alt="りょう｜未来投資navi" width="72" height="72">
      <div class="author-info">
        <h4>りょう｜未来投資navi</h4>
        <p>FP資格保有の現役投資家。自己資産4,000万円・<strong>運用益1,000万円以上</strong>の実績をもとに、50〜60代の投資初心者に向けた「守りながら増やす」資産設計を提案。YouTubeチャンネル「未来投資navi」で発信中。</p>
      </div>
    </div>"""

def page(title, category_label, charcount, lead_html, toc_items, body_html, seo_note,
         desc, keywords, slug, section, hero_name, extra_jsonld=None):
    jl = [jsonld_article(title, desc, slug, hero_name), jsonld_breadcrumb(title, slug)]
    if extra_jsonld:
        jl.append(extra_jsonld)
    h = head(title, desc, keywords, slug, section, hero_name, jl)
    toc = "\n".join(f'        <li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc_items)
    hero_alt = esc(title)
    return f"""{h}
<body>
  <div class="container">

    <div class="hero-image">
      <img src="./{hero_name}" alt="{hero_alt}" width="1280" height="720">
    </div>

    <header class="article-header">
      <span class="article-category">{category_label}</span>
      <h1 class="article-title">{esc(title)}</h1>
      <div class="article-meta">
        <span>未来投資navi 編集部</span>
        <span>{DATE_JP}</span>
        <span>約{charcount}字</span>
      </div>
    </header>

    <div class="lead">
      {lead_html}
    </div>

{YT_BANNER}

    <nav class="toc">
      <div class="toc-title">この記事の目次</div>
      <ol>
{toc}
      </ol>
    </nav>

    <article>
{body_html}

{cta_box(CTA_H, CTA_B)}
    </article>

{AUTHOR}

    <div class="seo-note">
      採用キーワード: {esc(seo_note)}
    </div>

  </div>
</body>
</html>
"""

CTA_H = "あなただけの投資設計図が必要ですか？"
CTA_B = ("今日お伝えしたのは一般論です。あなたの家族構成・年金額・資産状況・ライフプランによって、"
         "最適な現金比率・投資配分・取り崩しのタイミングはまったく変わります。"
         "現在、50〜60代向けの無料相談を毎月5名様限定で実施中です。ご興味のある方はお早めにどうぞ。")

# ============================================================== ARTICLE 1
a1_slug = "inflation-investment-strategy"
a1_hero = "blog_inflation_strategy_header.png"
a1_title = "現金は静かに溶ける｜50代60代がインフレに勝ち“上位25%”に入る最強の投資戦略【新NISA×オルカン】"
a1_desc = ("インフレで現金の価値が目減りする時代。50代60代が“債券中心”という古い常識を捨て、"
           "オルカン1本×新NISAで日本人の上位25%に入る方法を、現役FPがシミュレーション付きで解説します。")
a1_kw = "インフレ 投資 50代 60代, オルカン 新NISA, 現金 目減り, 上位25% 資産形成, 生活防衛資金, バーモントカレー オルカン"
a1_seonote = "インフレ 投資 50代 60代 / オルカン 新NISA 1800万円 / 現金 目減り 対策 / 上位25% 資産形成 / 生活防衛資金 2年分"

a1_lead = ('<p>「いい歳をしてお金を増やしたいなんて浅ましいのでは…」——そんなふうにブレーキを踏んでいませんか。'
           'はっきり言います。お金を増やしたいという欲は、まったく自然で当然のものです。'
           'そしていま、現金のまま置いておくことこそが一番のリスクになっています。'
           'この記事では、50代60代が<strong>インフレに負けず、オルカン1本×新NISA</strong>で'
           '“日本人の上位25%”に入るための考え方を、僕が普段の相談でお伝えしている内容そのままにお話しします。</p>')

a1_toc = [
    ("s1", "なぜ今「現金のまま」が一番危険なのか"),
    ("s2", "50代60代こそ「債券中心」をやめて株式中心で攻める理由"),
    ("s3", "プロはスパイスを足す。でもあなたは「オルカン1本」でいい"),
    ("s4", "今は歴史上もっとも有利な「超イージーモード」"),
    ("s5", "新NISA1,800万円をオルカンで埋めるとどうなる？"),
    ("s6", "まとめ：今日やるべきたった1つのこと"),
]

a1_body = f"""
      <h2 id="s1">なぜ今「現金のまま」が一番危険なのか</h2>
{svg_panel("現金は“静かに”価値が目減りする", [("物価はこの5年で約+10%", "食料品に限れば約+20%"), ("預金金利0.2〜0.5%では追いつかない", "差し引き毎年お金の価値が減っていく")], "#1a1020", "#3a1a2a", accent="#f5a0a0", rowfill="#3a1820", rowstroke="#a05060", subcol="#d8a0a0")}
      <p>50代60代の方なら、日々の買い物で「あれ、いつの間にこんなに高くなったの？」とゾッとすることがあるはずです。昔は150円だった卵が300円に、2,000円だったお米が4,000円台に。42年間ずっと10円だったうまい棒ですら、たった2年で15円になりました。</p>
      <p>大きな買い物はもっと深刻です。20年前に約236万円で買えたプリウスは、いま約350万円から。当時2,500万円で建てられた家は、いまや4,000万円コースです。僕たちの年収はほとんど増えていないのに、モノの値段だけがはるか遠くへ行ってしまいました。</p>
      <div class="info-box">
        <p>インフレは「真夏のアイスクリーム」です。昔はそこまで早く溶けませんでしたが、今の強烈な暑さ（＝インフレ）では、現金という名のアイスがみるみる溶けていきます。</p>
      </div>
      <p>総務省の消費者物価指数を見ると、ここ5年で物価は約10%上がっています。つまり銀行に1,000万円を置いて安心していた人は、数字は1,000万円のままでも、実際には<strong>900万円分のモノしか買えなくなっている</strong>ということです。通帳の数字は減らないのに、買えるものが静かに減っていく。これがインフレの本当の怖さです。</p>

      <h2 id="s2">50代60代こそ「債券中心」をやめて株式中心で攻める理由</h2>
      <p>銀行の窓口や昔ながらのファイナンシャルプランナーは、「もう50代ですから、株を減らして安全な債券を中心にしましょう」と勧めてきます。債券投資そのものは間違いではありません。ただ<strong>今の強いインフレ時代に「債券中心」にするのは、現代の経済環境を無視した提案</strong>だと僕は考えています。</p>
      <p>そもそも生の国債はリターンが低いうえに新NISAの対象外。「では新NISAで買える債券ファンドなら」と思っても、金利変動で元本割れするリスクがあります。リターンが低いのに減る可能性はある——それなら株式を中心に据えたほうが、よほど合理的です。</p>
      <div class="emphasis-box">
        <p>価格が動かない現金や債券は、インフレ下では「静かに、確実に価値が目減りしていく資産」に変わります。物価上昇に合わせて企業の利益が伸びる株式こそ、インフレへの最強の防具です。</p>
      </div>
      <p>「株は値下がりが怖い」——その不安にもちゃんと答えがあります。世界中の企業に<strong>長期・分散・積立</strong>で投資しておけば、企業はインフレに合わせて値段を上げていくので、株価も基本的に物価と一緒に育っていきます。沈まないけれど縮んでいくイカダ（債券・現金）を捨てて、揺れるけれど確実に前へ進むクルーザー（株式）に乗り換える。その覚悟が、60代からでも十分に間に合います。</p>

      <h2 id="s3">プロはスパイスを足す。でもあなたは「オルカン1本」でいい</h2>
{svg_panel("オルカンは“黄金比のバーモントカレー”", [("世界中の企業に自動で分散", "時価総額に応じて比率も自動調整"), ("素人がスパイスを足すと不味くなる", "毎月分配型・高コストのテーマ型は罠")], "#112a1a", "#1a4a30", accent="#6acf90", rowfill="#1e5c38", rowstroke="#3a9a60", subcol="#a0d8b8")}
      <p>正直に言うと、僕自身のポートフォリオには日本株や新興国株、暗号資産まで入っています。でもこれは、お金の専門家として日々決算書を読み込み、夜中に相場をチェックし、大きなストレスと時間をかけて使いこなしている「スパイス」です。忙しい皆さんが真似をする必要はまったくありません。むしろ<strong>絶対に真似しないでください</strong>。</p>
      <p>そこで圧倒的におすすめなのが、全世界株式インデックス、いわゆる「オルカン」です。オルカンは、世界中の最高の頭脳が計算し尽くした“黄金比のバーモントカレー”のようなもの。今はアメリカが強いのでApple等が多めですが、将来インドが世界一になれば自動でインドの比率を増やしてくれます。自分で煮込まなくても、勝手に最高のカレーを作り続けてくれるシステムです。</p>
      <div class="info-box">
        <p>残念なのは、半端に知識をつけて「完成されたカレーに変な隠し味」を足してしまう人です。手数料2%近いテーマ型アクティブファンドや、元本を取り崩しているだけの「毎月分配型」は、複利というお金が増える最大のエンジンを自ら捨てる行為。スリルが欲しいなら遊園地のジェットコースターへどうぞ。</p>
      </div>

      <h2 id="s4">今は歴史上もっとも有利な「超イージーモード」</h2>
      <p>「自分にできるだろうか」と不安に思う必要はありません。今の個人投資家は、歴史上かつてないほどの“超イージーモード”にいます。最大の理由は、フィンテックによるとんでもない価格破壊です。</p>
      <table class="comparison-table">
        <thead><tr><th>項目</th><th>15年前（2010年頃）</th><th>現在</th></tr></thead>
        <tbody>
          <tr><td class="label">投信のコスト</td><td>年0.7〜0.8%（アクティブは1.5〜2.0%）</td><td>オルカン実質0.057%</td></tr>
          <tr><td class="label">購入時手数料</td><td>3%前後が珍しくない</td><td>0円</td></tr>
          <tr><td class="label">国内株の売買</td><td>対面で片道1万円超</td><td>主要ネット証券で0円</td></tr>
          <tr><td class="label">最低投資額</td><td>1万円から</td><td>100円から</td></tr>
          <tr><td class="label">税金</td><td>利益に約20%課税</td><td>新NISAで生涯1,800万円まで無期限非課税</td></tr>
        </tbody>
      </table>
      <p>仮に1,000万円を運用した場合、15年前なら年間7万〜15万円ものコストを毎年取られていました。それが今のオルカンなら年間約5,800円。これが20年30年と積み上がれば、最終的な差は数百万円単位になります。<strong>「手数料が安く、税金がかからない時代に生まれた」というだけで、圧倒的に有利</strong>なのです。</p>

      <h2 id="s5">新NISA1,800万円をオルカンで埋めるとどうなる？</h2>
{svg_panel("年利6%・ほったらかしのシミュレーション", [("5年で1,800万円→約2,093万円", "毎月30万円を積立"), ("15年後 約3,748万円 / 20年後 約5,016万円", "追加投資ゼロ、ただ寝かせるだけ")], "#0d1f35", "#1a3a5c", accent="#f5c842", rowfill="#1e3f6a", rowstroke="#4a8abf", subcol="#a8c8e0")}
      <p>全世界株式（MSCI ACWI）の設定来リターンは年率約8.82%ですが、ここでは保守的に<strong>年利6%</strong>で試算します。50代60代の資金力を活かし、新NISAの生涯非課税枠1,800万円を毎月30万円（年360万円）で5年かけて埋めるとします。</p>
      <div class="number-box">
        <h4>放置プレイのシミュレーション（年利6%）</h4>
        <div class="calculation">5年後：元本1,800万円 → 約<strong>2,093万円</strong>（ここで積立完了）</div>
        <div class="calculation">投資開始から15年後：約<strong>3,748万円</strong></div>
        <div class="calculation calculation-highlight">投資開始から20年後：約<strong>5,016万円</strong></div>
      </div>
      <p>元本1,800万円から1円も追加していないのに、寝かせておくだけで3,200万円以上の利益が生まれる計算です。しかも新NISAなので、この利益に本来かかる約640万円の税金が<strong>まるごとゼロ</strong>。これだけの仕組みが目の前に揃っているのに、やらない理由が見当たりません。</p>

      <h2 id="s6">まとめ：今日やるべきたった1つのこと</h2>
      <div class="summary-box">
        <h3>インフレ時代の資産形成 3つの核心</h3>
        <ol>
          <li style="margin-bottom: 12px;"><strong>お金を増やす欲を肯定する</strong><br>現金のまま放置するのは、インフレ下では“静かに貧しくなる”選択。まず一歩を踏み出す。</li>
          <li style="margin-bottom: 12px;"><strong>50代60代でも株式中心で攻める</strong><br>債券中心という古い常識を捨て、長期・分散・積立でインフレに勝つ。</li>
          <li><strong>余計なスパイスを足さず「オルカン1本」</strong><br>超イージーモードの今、新NISA×オルカンを淡々と。浮いた時間は本業と家族に使う。</li>
        </ol>
      </div>
      <p>最後に、今日からできる具体的なアクションを1つだけ。<strong>今夜、ご自身の「毎月の生活費の2年分」を正確に計算してみてください。</strong>この2年分が、どんな暴落が来ても手をつけない「生活防衛資金」になります。この分厚いクッションがあるからこそ、株式の値動きに耐えられます。そして防衛資金と直近で使うお金を除いた余剰資金は、株式という最強のエンジンに回す覚悟を決めましょう。</p>
"""

# ============================================================== ARTICLE 2
a2_slug = "new-nisa-2026-3-actions"
a2_hero = "blog_new_nisa_2026_header.png"
a2_title = "2026年の新NISAで絶対にやるべき3つのこと｜“株だけ”が危ない時代の守りながら攻める戦略"
a2_desc = ("2026年は投資のルールが変わる転換点。米国株の歴史的割高・AIの収益ギャップ・債券の復権を踏まえ、"
           "50代60代が新NISAで絶対にやるべき3つのアクションを、現役FPがデータとともに解説します。")
a2_kw = "新NISA 2026, やるべきこと, 資産配分 見直し, 債券 復権, リスク許容度, バフェット指数 シラーPER, TINA TARA"
a2_seonote = "新NISA 2026 やるべきこと / 資産配分 見直し 50代60代 / 株式リスクプレミアム 消滅 / 債券 復権 / リスク許容度 最大下落幅"

a2_lead = ('<p>「オルカンの積立設定はもう済ませた。あとは寝て待つだけでしょ？」——もしそう思っているなら、'
           '一度立ち止まってください。<strong>2026年は、過去数年の“勝ちパターン”が通用しなくなる構造的な転換点</strong>になりうる年です。'
           'ただし、正しく準備すれば何も恐れることはありません。米国株の割高、AIの収益ギャップ、債券の復権という3つの変化を踏まえ、'
           '50代60代が新NISAで「絶対にやるべき3つのこと」を、データとともに整理します。</p>')

a2_toc = [
    ("s1", "なぜ2026年が「特別な年」なのか（TINA→TARA）"),
    ("s2", "やるべきこと①：資産配分を一度現実的に見直す"),
    ("s3", "やるべきこと②：自分の投資の「目的」を明確にする"),
    ("s4", "やるべきこと③：リスク資産を追いかけない"),
    ("s5", "まとめ：恐れず準備すればチャンスに変わる"),
]

a2_body = f"""
      <h2 id="s1">なぜ2026年が「特別な年」なのか（TINA→TARA）</h2>
{svg_panel("TINA から TARA へ", [("旧：There Is No Alternative", "株しか選択肢がなかった時代"), ("新：There Are Reasonable Alternatives", "国債で4%超、合理的な代替が存在")], "#0d1f35", "#1e4a78", accent="#8ab8d8", rowfill="#1e3f6a", rowstroke="#4a8abf", subcol="#a8c8e0")}
      <p>ここ10年、相場を支配してきたのは「とりあえずS&P500」「米国テック一極集中」という必勝パターンでした。それを支えたのが<strong>TINA（株以外に選択肢はない）</strong>という考え方です。低金利で債券は雀の涙、現金はインフレで目減りする。だから消去法で株を買うしかなかったわけです。</p>
      <p>しかし2026年、状況は<strong>TARA（合理的な代替案が存在する）</strong>へと変わりつつあります。理由は3つ。①米国株のバリュエーションが歴史的な極値にあること、②AIへの巨額投資に対して実際の収益が追いついていないこと、③国債で4%超の利回りが得られ、株式のうまみが数字の上で薄れていること。ゲームのルールそのものが変わろうとしているのです。</p>

      <h2 id="s2">やるべきこと①：資産配分を一度現実的に見直す</h2>
      <p>1つ目は、資産配分を現実的に見直すこと。これは逃げではなく、数字が示す有利な場所にお金を移すという積極的な判断です。まずは今の米国株がどれほど高い水準にあるか、具体的な指標で見てみましょう。</p>
      <table class="comparison-table">
        <thead><tr><th>指標</th><th>2026年初の水準</th><th>意味</th></tr></thead>
        <tbody>
          <tr><td class="label">バフェット指数</td><td>約230%</td><td>ITバブル期(約150%)を大きく超過</td></tr>
          <tr><td class="label">シラーPER</td><td>約40倍</td><td>30倍超は歴史的に調整の前兆</td></tr>
          <tr><td class="label">フォワードPER</td><td>約22.4倍</td><td>14%の高い利益成長を前提にした楽観値</td></tr>
          <tr><td class="label">株式益利回り vs 米10年債</td><td>約3.2% vs 約4.17%</td><td>リスクを取る株より国債が有利＝ERP消滅</td></tr>
        </tbody>
      </table>
      <p>注目すべきは一番下の行です。リスク資産である株式の期待リターンを、リスクのない国債の利回りが上回っている。<strong>リスクを取っているのにリターンが低い</strong>という、いわばバグのような状態です。だからこそ合理的な投資家は、株から債券などの確定利付資産へ資金をシフトし始めています。</p>
      <div class="emphasis-box">
        <p>特に50代60代の方は、ポートフォリオに債券というクッションを組み入れることを検討してください。「株式だけでは不安で夜も眠れない」という方ほど、守りの資産が効いてきます。</p>
      </div>

      <h2 id="s3">やるべきこと②：自分の投資の「目的」を明確にする</h2>
      <p>2つ目は原点回帰、投資の目的をはっきりさせることです。もしあなたの目的が15年後にお金を増やすことで、当面使う予定のない完全な余剰資金なら、今年株価が30%下がろうが過度に恐れる必要はありません。歴史的に見れば、長期で回復し増えている可能性が高いからです。</p>
      <p>問題はここからです。理屈では分かっていても、特に資産額が大きくなった50代60代にとって、一時的な暴落は精神的にめちゃくちゃ堪えます。資産が溶けていく恐怖は本能的なものだからです。</p>
      <div class="warning-box">
        <p>新NISAで貯めた1,000万円が、ある日500万円になっても平気でいられますか？「老後の計画が狂う」と感じるなら、それはリスクを取りすぎています。<strong>あらかじめ“耐えられる最大下落幅”を決めておく</strong>こと。自分の心と資産が壊れないラインを知ることが、2026年はさらに重要になります。</p>
      </div>
      <p>もし「現金を銀行で遊ばせておくのはもったいない」と感じるなら、その現金を①でお話しした債券に回すのも有効です。株が下がったときに債券がクッションになり、金利収入も生んでくれます。</p>

      <h2 id="s4">やるべきこと③：リスク資産を追いかけない</h2>
{svg_panel("集中から分散へ・守りの脇役を持つ", [("米国一強の神話に依存しない", "欧州・新興国・日本へ分散先を広げる"), ("金は“守り”、ビットコインはサテライト", "理解できない資産に手を出すのはギャンブル")], "#1a1205", "#2a2010", accent="#f5c842", rowfill="#2a1e08", rowstroke="#c8961e", subcol="#c8a060")}
      <p>3つ目は、値上がりしているリスク資産を追いかけないこと。米国株を牽引してきた一部の巨大テック企業は、利益（EPS）の成長率が鈍化傾向にあります。一方でそれ以外の企業は若干伸びる見込み。つまり「一部の勝ち組だけが勝ち続ける相場」から、<strong>資金が全体に循環する相場・選別される相場</strong>へ変わる可能性があります。</p>
      <p>だからこそ、S&P500だけでなく欧州・新興国・日本へ分散先を広げること。そして金などの現物資産も守りとして有効です。中央銀行が金を買い集めている今、個人が少し持たない理由はありません。</p>
      <div class="info-box">
        <p>ビットコインは分散先の一つとして“アリ”ですが、あくまでリスク資産。有事の安全資産ではなく、株が暴落する局面では一緒に下がる可能性が高いです。持つなら<strong>サテライト枠で少額を長期ホールド</strong>、これくらいの距離感がちょうどいいでしょう。銀やプラチナのように、よく分からないまま「上がりそうだから」と手を出すのは投資ではなくギャンブルです。</p>
      </div>

      <h2 id="s5">まとめ：恐れず準備すればチャンスに変わる</h2>
      <div class="summary-box">
        <h3>2026年の新NISAで絶対にやるべき3つのこと</h3>
        <ol>
          <li style="margin-bottom: 12px;"><strong>資産配分を現実的に見直す</strong><br>米国株の割高・AIの収益ギャップ・リスクプレミアムの消滅を踏まえ、債券など守りの資産を取り入れる。TINAは終わり、TARAの時代。</li>
          <li style="margin-bottom: 12px;"><strong>投資の目的を明確にする</strong><br>超長期の余剰資金ならドッシリ構える。耐えられないなら今すぐリスクを落とす。最大下落幅を先に決める。</li>
          <li><strong>リスク資産を追いかけない</strong><br>テーマ株・セクター集中を避け、地域・資産で分散。金は守り、ビットコインはサテライトで。</li>
        </ol>
      </div>
      <p>2026年は間違いなく難しい相場になります。でも今日の内容を理解して準備しておけば、多くの人がパニックになっているときに冷静にチャンスを拾える——そんな賢明な投資家になれるはずです。</p>
"""

# ============================================================== ARTICLE 3 (FAQ)
a3_slug = "60s-investment-qa"
a3_hero = "blog_60s_investment_qa_header.png"
a3_title = "【FPが本音で回答】60歳の投資初心者によくある相談10選｜“お金はあるのに正解がわからない”人へ"
a3_desc = ("お金はあるのに正解がわからない――60代の投資初心者から実際に受けた相談10個に、現役FPが本音で回答。"
           "インフレ・株式100%・一括投資・債券と金の役割まで、老後資金の不安をまとめて解消します。")
a3_kw = "60代 投資 相談, 投資初心者 60歳, 株式100% 大丈夫, 一括投資 積立, 新NISA 60代, ネット証券 60代"
a3_seonote = "60代 投資 相談 10選 / 投資初心者 60歳 / 株式100% 大丈夫か / 一括投資 積立 / 債券 金 役割 / ネット証券 60代"

a3_lead = ('<p>毎月、60〜65歳の投資初心者の方からたくさんのご相談をいただきます。そこで気づいた共通点があります。'
           'それは<strong>「お金はある。でも正解がわからない」</strong>ということ。'
           '若い世代の「お金がない」という悩みとは正反対で、まとまった資金があるからこそ身動きが取れないのです。'
           'この記事では、実際に多かった相談10個に本音で回答します。気になる質問だけ目次から読んでもOKです。</p>')

# (question_for_toc, anchor, full_question_heading, answer_html, faq_short_answer)
a3_items = [
    ("インフレが怖い。現金のままで大丈夫？", "q1",
     "Q1. インフレが怖いです。このまま現金で持っていて大丈夫ですか？",
     ("<p>結論、現金だけで持っているのは今の時代マジで危険です。インフレ率3%に対し預金金利は0.2〜0.5%程度。差し引き毎年2.5%ずつ価値が減り、1,000万円は10年後に実質780万円ほどの価値になる計算です。通帳の数字は変わらないのに、買えるモノが減っていく。これがインフレの怖さです。</p>"
      "<div class=\"info-box\"><p>ただし60代は「守り」も大切。慌てて色々な商品を買うと失敗します。一定の現金は必要です。<strong>焦らず、自分の状況を整理してから動く</strong>こと。具体策はこの後の質問で順番にお答えします。</p></div>"),
     "現金だけは危険です。インフレ3%・預金0.5%なら毎年2.5%価値が目減りし、1,000万円は10年で実質780万円ほどに。ただし60代は守りも大切で一定の現金は必要。焦らず状況を整理してから動きましょう。"),
    ("投資したいけど損するのが怖い", "q2",
     "Q2. 投資したいけれど、マイナスになるのが怖いです",
     ("<p>最初に少し厳しめに言います。投資はそもそもリスクがあるものです。何かを得るには何かを引き受ける必要がある——ノーペイン・ノーゲイン。大きく増やしたいなら、一時的に減る額も大きくなります。「お金を一切減らさずに増やす」という発想自体が間違いなのです。</p>"
      "<p>だからこそ大切なのは、<strong>いくらまでのマイナスなら耐えられるかを自分の財布と照らし合わせ、その“覚悟”を決めること</strong>。インフレ対策だけなら堅実な方法もありますし、大きく増やしたいなら相応のリスクを取る。まず自分がどうしたいのかを明確にしてください。</p>"),
     "投資にリスクはつきもの。ノーペイン・ノーゲインで、減らさず増やすという発想自体が間違いです。いくらまでのマイナスなら耐えられるかを決め、覚悟を持つことが一番大切です。"),
    ("銀行や保険会社に勧められた商品はどう？", "q3",
     "Q3. 銀行や保険会社に勧められた商品、客観的にどうですか？",
     ("<p>正直に言うと、こういう相談が来ると身構えます。人が販売する以上そこには手数料が乗り、営業側は手数料の高い商品を勧めがちだからです。ネット証券なら購入時手数料0円の商品が、窓口を通すだけで約3%——1,000万円なら一括で30万円が販売会社に入ることもあります。さらに毎月の運用コストも引かれ続けます。</p>"
      "<div class=\"emphasis-box\"><p>結論、おすすめは圧倒的にネット証券です。60代でもSBI証券や楽天証券を普通に使っている方はたくさんいますし、電話サポートもあります。どうしても対面が安心なら止めはしませんが、<strong>窓口は手数料が割高になるという事実だけは理解した上で</strong>選んでください。</p></div>"),
     "窓口商品は手数料が割高になりがちです。ネット証券なら購入時0円の商品が、窓口だと約3%かかることも。60代でもネット証券で十分使えるので、圧倒的にネット証券をおすすめします。"),
    ("株式100%の運用で大丈夫？", "q4",
     "Q4. 株式100%の運用で大丈夫ですか？債券はいらない？",
     ("<p>答えは「投資する金額による」です。全資産に対して何%を運用に回すかをまず決めてください。貯金1,000万円の人が10万円投資するのと、貯金50万円の人が10万円投資するのではまったく意味が違います。</p>"
      "<p>その上で、投資初心者なら<strong>最初は株式100%で問題ない</strong>と考えています。ここでいう株式100%とは一社の株ではなく、S&P500やオルカンのように何百・何千社へ分散された“株式投資信託”のこと。中身はしっかり分散されています。リーマンショック級で一時的に半分になるリスクは理解しつつ、長期では株式が最も増えやすい。債券などのヘッジ資産が必要になるのは、大きな金額を運用する人だけです。</p>"),
     "投資する金額によります。初心者ならS&P500やオルカンなど分散された株式投資信託で株式100%でも問題ありません。債券などのヘッジ資産が必要になるのは大金を運用する人だけです。"),
    ("米国株は割高。今から買って大丈夫？", "q5",
     "Q5. 米国株は割高だと聞きました。今から買っても大丈夫？",
     ("<p>長期で持つなら、タイミングはそこまで気にしなくて大丈夫です。割安・割高を測るCAPEレシオで見ると今のS&P500は約40倍と歴史的に高い水準。でも実は2017年も2019年も2021年も「割高」と言われ続け、それでも株価は上がってきました。割高という言葉に振り回されて買えないのが、一番もったいないパターンです。</p>"
      "<p>とはいえ高値掴みの不安も分かります。そこで60代の方は、<strong>リスクを取れる範囲で初期にある程度まとめて投資し、以降はドルコスト平均法で毎月一定額を積み立てる</strong>のが最適。時間を分散させるだけで、高値掴みの恐怖はほぼなくなります。</p>"),
     "長期で持つならタイミングは気にしすぎなくて大丈夫。CAPE40倍でも過去ずっと割高と言われ上昇してきました。初期にある程度投資し、以降は毎月一定額の積立で時間を分散しましょう。"),
    ("まとまったお金はどう動かす？", "q6",
     "Q6. まとまったお金を、どう動かせばいいですか？",
     ("<p>大金を手にすると、人はつい一度に全額を動かしたくなります。でも一括投資はリスクが大きく、計画的にやるべきです。初心者が1,000万円をいきなり株式100%に入れるのは、絶対におすすめしません。</p>"
      "<p>どうしても一括で入れるなら、株式以外にも分散を。初心者なら<strong>株式50%・債券50%、国内50%・先進国50%の“4資産均等型バランスファンド”</strong>に一括も一つの手です。ただ僕の根本的な考えは、最初から大きく動かすこと自体にリスクがあるというもの。まずは数百万円だけ投資し、残りはコツコツ積立。そして「いつ・いくら取り崩すか」という出口まで含めて計画することが重要です。一人で難しければ、プロに相談する方法もあります。</p>"),
     "一括投資はリスクが大きく計画的に。初心者なら4資産均等型バランスファンドへの一括も一案です。まずは一部を投資し残りは積立、取り崩しの出口まで含めて計画しましょう。"),
    ("債券や金は買ったほうがいい？", "q7",
     "Q7. 債券や金は買ったほうがいいですか？",
     ("<p>債券や金は株式とは違う動きをしやすいので、あくまで株式の“リスクヘッジ”として持つものです。基本は株式で資産を作り、金額が大きくなってきた段階で金や債券を組み合わせ、暴落時の下落幅を小さくする。これが正しい順番です。</p>"
      "<div class=\"emphasis-box\"><p>注意したいのは、分散しすぎるとリターンも得られなくなること。各資産の“役割”を明確にしましょう。金は直近30年でこそS&P500に迫る勢いですが、200年の歴史では株式に到底及びません。<strong>あくまで株式が主役、金や債券は守りの脇役</strong>。割合は少なめがおすすめです。</p></div>"),
     "債券や金は株式のリスクヘッジ役。基本は株式で資産を作り、金額が大きくなったら組み合わせて下落幅を抑えます。分散しすぎは禁物で、株式が主役、金・債券は守りの脇役として少なめに。"),
    ("ネット証券は難しそうで不安", "q8",
     "Q8. ネット証券は難しそうで不安です",
     ("<p>結論から言い切ります。60代の方でもネット証券で全く問題ありません。サイトはどんどん使いやすくなっています。ネックになりやすいのは、セキュリティ強化による“ログインの面倒さ”と、最初の“積立設定”くらい。</p>"
      "<p>でもこれも<strong>一度やってしまえばあとは簡単</strong>。毎日画面を開くものでもなく、設定さえ済めば基本は放置でOKです。最初のログインや設定が不安なら、サポート窓口を使うか、操作の手助けを頼ってください。それさえ越えれば、あとはずっとあなたの味方になります。</p>"),
     "60代でもネット証券で全く問題ありません。ネックはログインと最初の積立設定くらいで、一度やれば後は放置でOK。不安ならサポート窓口や操作の手助けを使いましょう。"),
    ("親が短命。自分も長く生きないかも", "q9",
     "Q9. 親が短命でした。自分も長生きしない前提でいい？",
     ("<p>結論、<strong>「自分は90歳以上生きる」前提で資産形成をすべき</strong>です。余命は誰にも分かりません。お金を持ったまま亡くなるのは仕方ないとしても、長生きしたのにお金がない“老後破綻”だけは避けなければいけません。今は100歳まで生きる人がゴロゴロいる時代です。</p>"
      "<p>同時に大切なのが「お金を使う計画」。『DIE WITH ZERO』には、余命宣告を受けて初めてお金より家族との時間を大事にするようになった夫婦の話が出てきます。短命かもと思うならなおさら“今”を大切に。<strong>貯める計画と使う計画を両方立てる</strong>のがベストです。</p>"),
     "余命は誰にも分からないので、90歳以上生きる前提で資産形成を。老後破綻だけは避けましょう。同時に『DIE WITH ZERO』のように使う計画も立て、今を大切にすることが大事です。"),
    ("結局、何をいついくら買えばいい？", "q10",
     "Q10. 結局、何を・いつ・いくら買えばいいですか？",
     ("<p>最終的に全員が聞いてくる質問です。お答えします。</p>"
      "<ul><li><strong>何を：</strong>初心者ならS&P500かオルカン。幅広く分散された株式インデックスファンドが王道です。</li>"
      "<li><strong>いつ：</strong>「今すぐ」です。1日でも早く市場にお金をさらすほど、複利で指数関数的に伸びます。</li>"
      "<li><strong>いくら：</strong>「一括＋積立」で設計します。働いている間は毎月“一定額”を積立（金額は変えない）。一括は今リスクを取れる範囲で、できるだけ初期に多めに入れるのがポイントです。</li></ul>"
      "<div class=\"warning-box\"><p>積立は<strong>生活防衛費の1年分を確保した上で</strong>続けてください。積立中に防衛費が減るなら、それは投資にお金を回しすぎです。リタイア時にも1年分の防衛費が残る設計を。</p></div>"),
     "何を=初心者はS&P500かオルカン。いつ=今すぐ。いくら=一括＋積立で設計し、毎月一定額を積立、一括は初期に多めに。生活防衛費1年分を確保した上で続けることが鉄則です。"),
]

a3_toc = [(anchor, qfor) for (qfor, anchor, _, _, _) in a3_items]

# build body for article 3 with a couple of SVG dividers
a3_parts = []
a3_parts.append(svg_panel("60代の共通点：お金はある、でも正解がわからない", [("若い世代＝時間はあるがお金がない", "答えは“給料の一部を積立”で明確"), ("60代＝まとまった資金があるから動けない", "だからこそ正しい順番が大切")], "#0d1f35", "#1a3a5c", accent="#f5c842", rowfill="#1e3f6a", rowstroke="#4a8abf", subcol="#a8c8e0"))
for idx, (qfor, anchor, qhead, ans, _) in enumerate(a3_items):
    a3_parts.append(f'      <h2 id="{anchor}">{qhead}</h2>')
    a3_parts.append("      " + ans)
    if idx == 4:  # 中盤にSVGを挿入
        a3_parts.append(svg_panel("迷ったら“順番”で考える", [("①まず生活防衛資金を確保", "②株式インデックスで土台を作る"), ("③金額が増えたら守りの資産を足す", "④出口（取り崩し）まで計画する")], "#112a1a", "#1a4a30", accent="#6acf90", rowfill="#1e5c38", rowstroke="#3a9a60", subcol="#a0d8b8"))
a3_parts.append('      <h2 id="ed">まとめ：今日やるなら、たった1つの行動を</h2>')
a3_parts.append('      <div class="summary-box"><h3>60代の投資、ここだけ押さえる</h3><ol>'
                '<li style="margin-bottom:12px;"><strong>現金だけは危険、でも守りの現金も必要</strong><br>焦らず、生活防衛費を土台にする。</li>'
                '<li style="margin-bottom:12px;"><strong>初心者はオルカン/S&P500で株式中心</strong><br>一括＋積立で時間を分散する。</li>'
                '<li><strong>金・債券は金額が増えてからの脇役</strong><br>90歳以上生きる前提で、使う計画も立てる。</li></ol></div>')
a3_parts.append('      <p>今日の動画…ではなく記事を踏まえて、一つだけ行動するなら<strong>「ネット証券の口座開設」</strong>です。口座を作るだけなら1円もかかりません。でもこの一歩で、間違いなく景色がガラッと変わります。</p>')
a3_body = "\n".join(a3_parts)

# ============================================================== WRITE
def write_article(slug, hero, title, cat, charcount, lead, toc, body, seonote, desc, kw, section, faq=None):
    extra = jsonld_faq(faq) if faq else None
    html = page(title, cat, charcount, lead, toc, body, seonote, desc, kw, slug, section, hero, extra_jsonld=extra)
    d = ROOT / "blog/2026" / slug
    (d / f"{slug}.html").write_text(html, encoding="utf-8")
    shutil.copy(PROFILE_SRC, d / "blog_profile_ryo.jpg")
    if not (d / hero).exists():
        shutil.copy(HERO_SRC, d / hero)  # 仮置き（要差し替え）
    print(f"wrote {slug}.html ({len(html)} chars)")

write_article(a1_slug, a1_hero, a1_title, "インフレ対策", "3,000", a1_lead, a1_toc, a1_body, a1_seonote, a1_desc, a1_kw, "資産形成")
write_article(a2_slug, a2_hero, a2_title, "新NISA戦略", "2,900", a2_lead, a2_toc, a2_body, a2_seonote, a2_desc, a2_kw, "新NISA")
faq = [(it[2].split(". ",1)[1] if ". " in it[2] else it[2], it[4]) for it in a3_items]
write_article(a3_slug, a3_hero, a3_title, "老後の資産形成", "3,400", a3_lead, a3_toc, a3_body, a3_seonote, a3_desc, a3_kw, "資産運用", faq=faq)
print("DONE")

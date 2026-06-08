# -*- coding: utf-8 -*-
"""1人語り台本 → blog/2026/ 記事 変換（第2弾: ほったらかし / FANG+vs S&P500 / 日本株）。
build_solo_articles.py と同じ構成。og:image は実画像に合わせ1024x576。"""
import re, shutil
from pathlib import Path

ROOT = Path("/Users/satoshioka/mirai-toushi-navi")
TPL = ROOT / "blog/2026/index-vs-individual-stock/index-vs-individual-stock.html"
DATE_ISO = "2026-05-27"; DATE_JP = "2026年5月27日"
BASE = "https://eva-solution.netlify.app"
YT = "https://www.youtube.com/channel/UCb-u1hcuQyo7qruBhuiOBZg"
LINE = "https://lin.ee/FxIOpk1"

tpl = TPL.read_text(encoding="utf-8")
STYLE = re.search(r"<style>.*?</style>", tpl, re.DOTALL).group(0)
YT_BANNER = re.search(r"(<a class=\"youtube-channel-banner\".*?</a>)", tpl, re.DOTALL).group(1)
PROFILE_SRC = TPL.parent / "blog_profile_ryo.jpg"
HERO_SRC = TPL.parent / "blog_index_vs_individual_stock_header.webp"

GA = """    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-K4EG9Q6FL6"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        gtag('js', new Date());
        gtag('config', 'G-K4EG9Q6FL6');
    </script>"""

def esc(s):
    return s.replace("&","&amp;").replace('"',"&quot;").replace("<","&lt;").replace(">","&gt;")

def head(title, desc, keywords, slug, section, hero, jl):
    url=f"{BASE}/blog/2026/{slug}/{slug}.html"; img=f"{BASE}/blog/2026/{slug}/{hero}"
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
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{img}">
  <meta property="og:image:width" content="1024">
  <meta property="og:image:height" content="576">
  <meta property="og:image:alt" content="{esc(title)}">
  <meta property="og:site_name" content="未来投資navi">
  <meta property="article:published_time" content="{DATE_ISO}">
  <meta property="article:author" content="りょう">
  <meta property="article:section" content="{esc(section)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@investment_navi">
  <meta name="twitter:creator" content="@investment_navi">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{img}">
  <meta name="twitter:image:alt" content="{esc(title)}">
{jl}
{STYLE}
</head>"""

def jl_article(title, desc, slug, hero):
    url=f"{BASE}/blog/2026/{slug}/{slug}.html"; img=f"{BASE}/blog/2026/{slug}/{hero}"
    return f"""  <script type="application/ld+json">
  {{ "@context":"https://schema.org","@type":"Article","headline":"{esc(title)}","description":"{esc(desc)}","image":"{img}","author":{{"@type":"Person","name":"りょう"}},"publisher":{{"@type":"Organization","name":"未来投資navi","logo":{{"@type":"ImageObject","url":"{BASE}/images/logo.png"}}}},"datePublished":"{DATE_ISO}","dateModified":"{DATE_ISO}","mainEntityOfPage":{{"@type":"WebPage","@id":"{url}"}} }}
  </script>"""

def jl_bc(title, slug):
    url=f"{BASE}/blog/2026/{slug}/{slug}.html"
    return f"""  <script type="application/ld+json">
  {{ "@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"ホーム","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"ブログ","item":"{BASE}/blog/"}},{{"@type":"ListItem","position":3,"name":"{esc(title)}","item":"{url}"}}] }}
  </script>"""

def svg_panel(title, rows, c1, c2, accent="#f5c842", rowfill="#1e3f6a", rowstroke="#4a8abf", subcol="#a8c8e0"):
    gid="g"+str(abs(hash((title,c1,c2)))%100000); n=len(rows)
    p=[f'<svg viewBox="0 0 720 405" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(title)}">',
       f'<defs><linearGradient id="{gid}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:{c1}"/><stop offset="100%" style="stop-color:{c2}"/></linearGradient></defs>',
       f'<rect width="720" height="405" fill="url(#{gid})"/>',
       f'<text x="360" y="74" font-family="\'Hiragino Kaku Gothic ProN\',\'Hiragino Sans\',sans-serif" font-size="20" font-weight="bold" fill="#eef4fb" text-anchor="middle">{esc(title)}</text>']
    if n:
        bh=56; gap=14; tot=n*bh+(n-1)*gap; y0=200-tot//2+18
        for i,(b,s) in enumerate(rows):
            y=y0+i*(bh+gap)
            p.append(f'<rect x="120" y="{y}" width="480" height="{bh}" rx="8" fill="{rowfill}" stroke="{rowstroke}" stroke-width="1.5"/>')
            p.append(f'<text x="360" y="{y+24}" font-family="\'Hiragino Kaku Gothic ProN\',\'Hiragino Sans\',sans-serif" font-size="16" fill="{accent}" text-anchor="middle" font-weight="bold">{esc(b)}</text>')
            if s: p.append(f'<text x="360" y="{y+44}" font-family="\'Hiragino Kaku Gothic ProN\',\'Hiragino Sans\',sans-serif" font-size="12.5" fill="{subcol}" text-anchor="middle">{esc(s)}</text>')
    p.append("</svg>")
    return '<div class="section-visual">'+"".join(p)+"</div>"

CTA_H="あなただけの投資設計図が必要ですか？"
CTA_B=("今日お伝えしたのは一般論です。あなたの家族構成・年金額・資産状況・ライフプランによって、最適な現金比率・投資配分・取り崩しのタイミングはまったく変わります。現在、50〜60代向けの無料相談を毎月5名様限定で実施中です。ご興味のある方はお早めにどうぞ。")
def cta_box():
    return f"""      <div class="cta-box">
        <h3>{CTA_H}</h3>
        <p>{CTA_B}</p>
        <a href="{LINE}" target="_blank" rel="noopener noreferrer" class="cta-button">公式LINEで無料相談する</a>
      </div>"""
AUTHOR=f"""    <div class="author-box">
      <img class="author-photo" src="./blog_profile_ryo.jpg" alt="りょう｜未来投資navi" width="72" height="72">
      <div class="author-info">
        <h4>りょう｜未来投資navi</h4>
        <p>FP資格保有の現役投資家。自己資産4,000万円・<strong>運用益1,000万円以上</strong>の実績をもとに、50〜60代の投資初心者に向けた「守りながら増やす」資産設計を提案。YouTubeチャンネル「未来投資navi」で発信中。</p>
      </div>
    </div>"""

def page(title, cat, cc, lead, toc, body, seonote, desc, kw, slug, section, hero):
    jl="\n".join([jl_article(title,desc,slug,hero), jl_bc(title,slug)])
    h=head(title,desc,kw,slug,section,hero,jl)
    toc_html="\n".join(f'        <li><a href="#{i}">{esc(t)}</a></li>' for i,t in toc)
    return f"""{h}
<body>
  <div class="container">
    <div class="hero-image">
      <img src="./{hero}" alt="{esc(title)}" width="1280" height="720">
    </div>
    <header class="article-header">
      <span class="article-category">{cat}</span>
      <h1 class="article-title">{esc(title)}</h1>
      <div class="article-meta"><span>未来投資navi 編集部</span><span>{DATE_JP}</span><span>約{cc}字</span></div>
    </header>
    <div class="lead">{lead}</div>

{YT_BANNER}

    <nav class="toc"><div class="toc-title">この記事の目次</div><ol>
{toc_html}
    </ol></nav>
    <article>
{body}

{cta_box()}
    </article>
{AUTHOR}
    <div class="seo-note">採用キーワード: {esc(seonote)}</div>
  </div>
</body>
</html>
"""

def write(slug, hero, title, cat, cc, lead, toc, body, seonote, desc, kw, section):
    html=page(title,cat,cc,lead,toc,body,seonote,desc,kw,slug,section,hero)
    d=ROOT/"blog/2026"/slug; d.mkdir(parents=True,exist_ok=True)
    (d/f"{slug}.html").write_text(html,encoding="utf-8")
    shutil.copy(PROFILE_SRC, d/"blog_profile_ryo.jpg")
    if not (d/hero).exists(): shutil.copy(HERO_SRC, d/hero)
    print(f"wrote {slug}.html ({len(html)} chars)")

# ===================== ARTICLE 4: ほったらかし
s4="60s-hands-off-investing"; h4="blog_60s_hands_off_header.webp"
t4="【60代の投資戦略】“ほったらかし”が最強の武器になる3つの理由｜新NISA×4%ルールで作る不安のない老後"
d4=("投資のテクニックは一切不要。60代こそ“ほったらかし投資”が最適解です。複利・稲妻が輝く瞬間・売買の罠という3つのデータに基づく理由と、新NISA×4%ルールの具体的な設計を、現役FPがわかりやすく解説します。")
k4="60代 ほったらかし投資, 複利 長期投資, 新NISA 4%ルール, 全世界株式, 稲妻が輝く瞬間, 60代 投資 失敗"
sn4="60代 ほったらかし投資 / 複利 効果 シミュレーション / 新NISA 年初一括 積立 / 4%ルール 取り崩し / 稲妻が輝く瞬間"
lead4=('<p>「難しいことは正直めんどくさい。証券口座にお金を入れて、勝手に増えてくれるならそれが一番」——その感覚、まったく正しいです。'
       '実は<strong>“ほったらかし”こそ、データで証明された投資の王道</strong>。とくに60代の初心者にとっては鉄板中の鉄板です。'
       'この記事では、なぜほったらかしが最強なのか、何をどう買えばいいのか、そして60代がやりがちな失敗まで、まるごとお話しします。</p>')
toc4=[("s1","なぜ“ほったらかし”が最強なのか（3つの理由）"),("s2","具体的に何を・どう買えばいいのか"),
      ("s3","出口設計：5年後から4%ルールで取り崩す"),("s4","60代がやりがちな2つの失敗"),("s5","まとめ：最初に考え、あとは触らない")]
body4=f"""
      <h2 id="s1">なぜ“ほったらかし”が最強なのか（3つの理由）</h2>
{svg_panel("ほったらかしが最強な3つの理由", [("①複利を中断させない","売った瞬間に複利の連鎖が切れる"),("②稲妻が輝く瞬間を逃さない","急騰の数日は暴落直後に来る"),("③売買するほど損をする","せっかちな人から辛抱強い人へ")], "#0d1f35","#1a3a5c")}
      <h3>① 複利を中断させない</h3>
      <p>複利とは「利益がまた利益を生む」仕組みです。100万円を年5%で運用すると、10年で約163万円、20年で約265万円、30年で約432万円。何もしなくても4倍以上になります。ところが途中で「不安だから一度売ろう」とやると、この複利の連鎖が切れてしまう。<strong>触らない・売らない・持ち続ける</strong>が複利を最大化する絶対条件です。</p>
      <h3>② 「稲妻が輝く瞬間」を逃さない</h3>
      <p>JPモルガンの調査（2002〜2021年のS&P500）が衝撃的です。</p>
      <table class="comparison-table">
        <thead><tr><th>投資行動</th><th>年率リターン</th><th>150万円が…</th></tr></thead>
        <tbody>
          <tr><td class="label">ずっと持ち続けた</td><td>9.52%</td><td>約925万円</td></tr>
          <tr><td class="label">最良の10日を逃した</td><td>5.33%</td><td>約424万円</td></tr>
          <tr><td class="label">最良の30日を逃した</td><td>0.41%</td><td>約163万円</td></tr>
        </tbody>
      </table>
      <p>たった10日逃すだけで利益が半分以下に。市場が急騰する「稲妻が輝く瞬間」は、しかも大暴落の直後に来ることが多いんです。怖いから売った瞬間、一番おいしいタイミングを逃す。ご飯を炊いている途中で蓋を開けるようなもの。<strong>市場に居続けること</strong>が最強です。</p>
      <h3>③ 売買するほど損をする</h3>
      <p>カリフォルニア大学の調査では、売買頻度が最も高いグループの年率11.4%に対し、最も低いグループは18.5%。何もしない人のほうが7%も高いリターンでした。理由は手数料・税金と、感情による高値づかみ・底値売り。投資の神様バフェットも「株式市場は、せっかちな人から辛抱強い人へお金を移す装置だ」と言っています。</p>
      <div class="emphasis-box"><p>裏ワザはありません。資産がマイナスになってもじっと耐え、何もしない人が一番儲かる。だから証券口座は見ないのが一番。蓋を開けなければ、美味しく炊けます。</p></div>

      <h2 id="s2">具体的に何を・どう買えばいいのか</h2>
      <p>結論、まず<strong>全世界株式に分散投資</strong>します。1本買うだけで数千社に分散でき、どの会社が伸びるか当てる必要もありません。過去30年で全世界株式は名目年率8%程度。インフレを引いても実質6%程度が期待できますが、ここでは控えめに<strong>年率5%</strong>で考えます。</p>
      <div class="number-box">
        <h4>新NISA「年初一括＋積立」ハイブリッド（年利5%）</h4>
        <div class="calculation">年初に240万円を一括＋毎月10万円を積立 × 5年 ＝ 元本1,800万円（満額）</div>
        <div class="calculation calculation-highlight">5年後の資産：おおよそ<strong>2,250万〜2,300万円</strong>（インフレ差引後）</div>
      </div>
      <p>特別なことは何もしていません。相場を読んだわけでもなく、ただ仕組みを作っただけ。これがほったらかしの正体です。</p>

      <h2 id="s3">出口設計：5年後から4%ルールで取り崩す</h2>
      <p>資産形成は「増やす」だけでは半分。<strong>「使う」まで設計して初めて完成</strong>です。ここでは5年後から<strong>4%ルール</strong>（資産の4%を毎年取り崩しても枯渇しにくい考え方）で使います。</p>
      <p>資産が2,270万円なら、その4%は年間約90万円＝月7.5万円ほど。年金の代わりではなく、年金を支えるもう一本の柱です。運用利回り5%・取り崩し4%なら差し引きまだ1%残るので、平均的には資産はほぼ減りません。温泉のお湯が常に流れている状態ですね。暴落の年もありますが、取り崩しまで設計してあれば慌てて売らずに済みます。</p>

      <h2 id="s4">60代がやりがちな2つの失敗</h2>
{svg_panel("60代がやりがちな2つの失敗", [("①慣れてYouTubeの“爆上げ”に誘惑","70歳で暴落＝取り崩し時に直撃"),("②いきなりリバランスで大金一括","時間分散できず高値づかみのリスク")], "#1a1020","#3a1a2a", accent="#f5a0a0", rowfill="#3a1820", rowstroke="#a05060", subcol="#d8a0a0")}
      <p><strong>失敗①：慣れてくると欲が出る。</strong>最初は「年金の足しになれば」で始めたのに、しばらくすると「オルカンだけじゃ物足りない」「もっと増やしたい」となり、YouTubeの「今が最後のチャンス」に乗ってハイリスク商品へ。もし70歳前後で暴落に巻き込まれれば、資産が減る局面で取り崩すことになります。<strong>最初に決めた計画は何があっても守る。</strong>楽しむ投資は必ず余剰資金で、生活費・老後資金とは完全に分けてください。</p>
      <div class="warning-box"><p><strong>失敗②：いきなりリバランス戦略で大金を一括投資。</strong>「オルカン50%・現金50%」を守ろうと1,500万円を一気に株へ——これは時間分散ができず、高値づかみのリスクを自分から許容している状態です。含み損が50万円と500万円、どちらが冷静でいられるかは明らかですよね。<strong>投資先の分散と時間の分散はセット</strong>です。</p></div>

      <h2 id="s5">まとめ：最初に考え、あとは触らない</h2>
      <div class="summary-box"><h3>ほったらかし投資の完成形</h3><ol>
        <li style="margin-bottom:12px;"><strong>全世界株式に分散投資</strong><br>複利・稲妻・売買の罠——データが「居続けること」の強さを示している。</li>
        <li style="margin-bottom:12px;"><strong>新NISAで年初一括＋積立のハイブリッド</strong><br>無理のない金額で。1,800万円を埋められなくても全く問題ない。</li>
        <li><strong>5年後から4%ルールで取り崩す</strong><br>増やすだけでなく使うまで設計する。慣れても欲張らない。</li>
      </ol></div>
      <p>ほったらかし投資の本質は「何もしない」ことではなく、<strong>最初にめちゃくちゃ考えて、あとは余計なことをしない</strong>こと。これが60代の初心者にとって一番現実的で、再現性の高い資産形成です。</p>
"""

# ===================== ARTICLE 5: FANG+ vs S&P500
s5="sp500-vs-fang-plus"; h5="blog_sp500_fang_header.webp"
t5="S&P500が下がってもFANG+は上がる？“デカップリング”の正体とAIインフラ・電力という本命【50代60代の戦い方】"
d5=("S&P500が下落する中、なぜFANG+だけ上がるのか。機関投資家が逃げ込む先と、AI革命の本当のボトルネック“電力インフラ”をやさしく解説。50代60代が老後資金を守るための立ち回り方を現役FPが整理します。")
k5="FANG+ S&P500 比較, デカップリング, AIインフラ 電力, 機関投資家 資金逃避, サテライト投資, 50代60代 暴落 対処"
sn5="FANG+ S&P500 違い / デカップリング 正体 / AIインフラ 電力 ボトルネック / 機関投資家 資金逃避 / サテライト投資 50代60代"
lead5=('<p>ずっと順調だったS&P500がズルズル下がる一方で、<strong>FANG+と呼ばれる少数の巨大テック企業だけは別の動き</strong>をしている——'
       'そんな“デカップリング（分離）”が起きています。なぜ同じアメリカ市場でこんなことが？そして老後資金を守る50代60代は、'
       'このニュースにどう向き合えばいいのか。結論を先に言うと、<strong>慌てて売らないこと、そして王道（長期・積立・分散）を崩さないこと</strong>です。</p>')
toc5=[("s1","なぜS&P500は下がり、FANG+は上がるのか"),("s2","短期の熱狂か？AIインフラという本命メガトレンド"),
      ("s3","電力こそ“AIの最大のボトルネック”"),("s4","50代60代の正しい立ち回り方"),("s5","まとめ")]
body5=f"""
      <h2 id="s1">なぜS&P500は下がり、FANG+は上がるのか</h2>
{svg_panel("同じ米国市場で起きた“分離”", [("S&P500：高金利・消費冷え込み・原油高で下落","伝統的な小売・消費財がダメージ"),("FANG+：戦争・インフレに強い少数銘柄が反発","物理的ダメージを受けにくい事業")], "#0d1f35","#1a3a5c")}
      <p>S&P500を構成する多くの企業は、戦争が起きる前から弱っていました。原因は高金利の長期化と消費の冷え込み。そこへ原油高というダメ押しが入り、コストばかりかさんで利益が削られたのです。レシピは変えていないのに仕入れ値だけが上がり続けるレストラン——そんな状態です。</p>
      <p>一方でFANG+のような一部のテック企業は反発しました。ポイントは「IT・AIだから」ではなく、<strong>戦争やインフレでも物理的にダメージを受けにくい、むしろ特需になる事業</strong>だったこと。たとえば動画配信（不況でも残る低コスト娯楽）、防衛AI（有事で予算増）、サイバーセキュリティ（どんなに苦しくても費用を削れない）。機関投資家はこうした「戦争に強い銘柄」へ資金を逃していたわけです。</p>

      <h2 id="s2">短期の熱狂か？AIインフラという本命メガトレンド</h2>
      <p>「それって戦争による短期の避難でしょ？」——半分は当たりです。FANG+はわずか10銘柄ほどの指数なので、一部の特需銘柄が押し上げただけ、という側面はあります。でもその奥には、マクロの悪化を吹き飛ばすほどの強烈なトレンドがありました。</p>
      <p>実はパニックの裏で、S&P500の内部では激しい資金の移動が起きていました。情報技術セクター全体はマイナスだったのに、最も上昇したのは<strong>公益事業（電力など）が+10%超、次いでエネルギー</strong>。地味なインフラがトップに立ったのです。</p>

      <h2 id="s3">電力こそ“AIの最大のボトルネック”</h2>
{svg_panel("AIの本当の根っこは「電力」", [("巨大ITのAI投資は年6,000億ドル規模","賢いAIも電力とサーバーがなければ動かない"),("AIの最大の制約はGPUではなく電力","原子力・再エネ・発電卸に資金が集中")], "#112a1a","#1a4a30", accent="#6acf90", rowfill="#1e5c38", rowstroke="#3a9a60", subcol="#a0d8b8")}
      <p>グーグルやアマゾンは今年だけでAIに6,000億ドル規模を投じると見られています。でも、どれだけ賢いAIを作っても、最後はそれを動かす膨大な電力と物理的なサーバー拠点がなければ動きません。だからこそ、AIデータセンターの電力需要を満たす<strong>電力インフラ（原子力・再エネ・発電卸）</strong>が「AIの本命」として強烈に再評価されました。AIの最大のボトルネックは、もはやGPU（半導体）ではなく電力なのです。</p>
      <div class="info-box"><p>ただしAIインフラも万能ではありません。最新半導体には中東産の特殊ガスが必要で、供給が断たれれば「作れない」リスクがあります。データセンターが物理攻撃を受けてダウンした例も。デジタルの覇者も、現実のインフラが壊れれば一瞬で足元をすくわれます。</p></div>

      <h2 id="s4">50代60代の正しい立ち回り方</h2>
      <p>ここが一番大切です。こうしたトレンドを知るのは投資家として大きな武器になりますが、<strong>だからといって個別銘柄に飛びつくのは禁物</strong>です。すでに株価に成長が織り込まれ、高値づかみになる可能性もあります。</p>
      <div class="warning-box"><p>本記事で触れた企業やセクターは、<strong>市場で起きている事実の紹介であって、特定銘柄の推奨ではありません。</strong>僕たちの投資の基本は、あくまで王道の「長期・積立・分散」。老後資金を守る手堅い運用（オルカンやS&P500のコア）は、ニュースで揺らがせないでください。</p></div>
      <p>そのうえで、もし時代のど真ん中を肌で感じたいなら、<strong>手堅い運用とは完全に別枠で、少額のサテライト投資</strong>として向き合うのはアリです。大切なのは、S&P500が下がったというニュースだけで老後資金を手放さないこと。市場の二極化の「なぜ」を理解していれば、不安に振り回されずに済みます。</p>

      <h2 id="s5">まとめ</h2>
      <div class="summary-box"><h3>デカップリング相場の歩き方</h3><ol>
        <li style="margin-bottom:12px;"><strong>S&P500下落とFANG+反発の正体</strong><br>機関投資家が「戦争に強い事業」とAIインフラへ資金を逃した結果。</li>
        <li style="margin-bottom:12px;"><strong>AIの本当のボトルネックは電力</strong><br>公益・電力インフラが本命として再評価された。ただし物理リスクもある。</li>
        <li><strong>コアは崩さない、サテライトは少額・別枠</strong><br>王道は長期・積立・分散。個別銘柄への集中投資は避ける。</li>
      </ol></div>
      <p>ニュースは不安を煽りますが、僕たちには僕たちの戦い方があります。一時的な値動きに振り回されず、コアを守り、知識はサテライトとして活かす。それが50代60代の賢い立ち回りです。</p>
"""

# ===================== ARTICLE 6: 日本株
s6="japan-stocks-2026"; h6="blog_japan_stocks_2026_header.webp"
t6="2026年は“日本株”を狙え｜円高リスクに備える為替ヘッジと、日経平均・TOPIXの選び方【50代60代向け】"
d6=("オルカンもS&P500も、実は外貨建て。円高が来れば株価が動かなくても資産は目減りします。2026年に日本株を“トッピング”して為替リスクを分散する理由と、日経平均・TOPIXの選び方を、現役FPが解説します。")
k6="日本株 2026, 為替ヘッジ 円高, 日経平均 TOPIX 違い, 円キャリートレード 巻き戻し, 自社株買い PBR, 全世界株式 日本株"
sn6="日本株 2026 / 為替ヘッジ 円高対策 / 日経平均 TOPIX 違い 選び方 / 円キャリートレード 巻き戻し / 全世界株式 日本株 トッピング"
lead6=('<p>「いつも全世界株式やS&P500を勧めてたのに、なんで日本株？」——その疑問、よく分かります。コアが全世界株式・S&P500でいいという考えは今も変わりません。'
       'でも忘れがちなのが、<strong>オルカンもS&P500も“外貨建て資産”</strong>だという事実。円高が来れば、株価が動かなくても資産は目減りします。'
       '2026年は、為替リスクを分散する“日本株トッピング”が効いてくる年だと考えています。</p>')
toc6=[("s1","なぜ2026年に日本株なのか（為替リスクの分散）"),("s2","円高シナリオを無視できない理由"),
      ("s3","日本株を動かす主役は誰か"),("s4","日経平均とTOPIX、どっちを買う？"),("s5","まとめ：あくまで“トッピング”として")]
body6=f"""
      <h2 id="s1">なぜ2026年に日本株なのか（為替リスクの分散）</h2>
{svg_panel("あなたの資産、円安に偏っていませんか？", [("オルカンもS&P500も外貨建て","円安で増え、円高で目減りする"),("1ドル150円→130円で約13%ダウン","株価が動かなくても資産は減る")], "#0d1f35","#1a3a5c")}
      <p>ここ数年、僕たちは歴史的な円安の恩恵を受けてきました。S&P500やオルカンを持っているだけで、株価上昇＋円安効果で資産が増えた。でもその含み益の一部は、単に円の価値が下がったことによるものです。つまり今、<strong>多くの人の資産は猛烈に「円安シナリオ」に偏っている</strong>のです。</p>
      <p>もし円高が進めば、1ドル150円が130円になるだけで、S&P500の株価が動かなくても資産価値は約13%ダウン。これを誤差と笑えるならいいですが、多くの人にとっては笑えないダメージです。だからこそ、為替の影響を直接受けない<strong>日本株</strong>が、リスクヘッジとして魅力的に見えてきます。</p>

      <h2 id="s2">円高シナリオを無視できない理由</h2>
      <p>「日米の金利差はまだ大きいから円安継続でしょ？」——基本シナリオはその通りです。でも最近、「金利差縮小＝円高」という教科書通りの相関が薄れ、円高の可能性も意外と無視できません。</p>
      <ul>
        <li><strong>日本の巨額債務と積極財政：</strong>政府債務はGDP比約230%。積極財政でさらに財政が悪化すれば「悪い円安」のリスク。</li>
        <li><strong>金利差の逆転は事実上不可能：</strong>米3.5〜3.75%に対し日本は0.5%前後。単純な金利差での円高は起きにくい。</li>
        <li><strong>円キャリートレードの巻き戻し：</strong>米国が急な景気後退で緊急利下げ→日本が利上げ、となると、低金利の円で借りてドル運用していた資金が一気に円買いに動き、<strong>急激な円高</strong>に。2024年夏の急落がまさにこれでした。</li>
      </ul>
      <div class="emphasis-box"><p>円安と円高、どちらに転ぶか分からない。だからこそ両方に備える。これが分散投資の真髄です。S&P500一本足だと「株安＋円高」の往復ビンタを食らいますが、日本株を持っていれば少なくとも為替のビンタは避けられます。</p></div>

      <h2 id="s3">日本株を動かす主役は誰か</h2>
{svg_panel("日本株を支える3つの力", [("海外投資家と自社株買い","個人は売り越し、海外勢と企業が買い"),("東証のPBR1倍是正・株主還元強化","ため込み体質からの脱却"),("積極財政＝国策の後押し","国策に売りなし")], "#1a1205","#2a2010", accent="#f5c842", rowfill="#2a1e08", rowstroke="#c8961e", subcol="#c8a060")}
      <p>意外かもしれませんが、日本株を動かすメインプレイヤーは海外投資家です。一方で日本の個人投資家はむしろ売り越し、新NISAでオルカンやS&P500を買っています。「人の行く裏に道あり花の山」——みんなが手放している今こそ、という見方もできます。</p>
      <p>もう一つの主役が<strong>企業自身の自社株買い</strong>です。東証からの「PBR1倍割れ是正」要請などを受け、ため込み体質だった日本企業が、資本効率の改善・株主還元・ガバナンス改革に本気で動き始めました。その結果、稼ぐ力がつき、日経平均がS&P500を上回る場面も出ています。積極財政という国策の後押しも、企業業績にはプラス材料です。</p>

      <h2 id="s4">日経平均とTOPIX、どっちを買う？</h2>
      <p>個別株は楽しいですが、忙しい方にはインデックスファンドが王道。日本株なら選択肢は<strong>日経平均かTOPIX</strong>の2択で十分です。</p>
      <table class="comparison-table">
        <thead><tr><th></th><th>日経平均株価</th><th>TOPIX（東証株価指数）</th></tr></thead>
        <tbody>
          <tr><td class="label">構成</td><td>代表225社・株価平均型</td><td>プライムほぼ全銘柄・時価総額加重</td></tr>
          <tr><td class="label">特徴</td><td>値がさ株の影響大・動きが大きい</td><td>分散が効く・動きはマイルド</td></tr>
          <tr><td class="label">向いている人</td><td>成長を牽引する主力に乗りたい</td><td>市場全体に幅広く分散したい</td></tr>
        </tbody>
      </table>
      <p>長期で見れば誤差の範囲なので、迷ったらコストが安い方・純資産総額が大きい方でOK（例：eMAXIS Slim 国内株式の日経平均型／TOPIX型）。あれこれ複雑な商品に手を出す必要はありません。ポートフォリオはシンプルなほど長続きします。</p>

      <h2 id="s5">まとめ：あくまで“トッピング”として</h2>
      <div class="summary-box"><h3>2026年・日本株の狙い方</h3><ol>
        <li style="margin-bottom:12px;"><strong>為替ヘッジとして日本株を強化</strong><br>円安・円高どちらに転んでもいいよう通貨を分散する。</li>
        <li style="margin-bottom:12px;"><strong>海外勢・自社株買い・国策が追い風</strong><br>個人が売っている今こそ逆張りの妙味。</li>
        <li><strong>商品は日経平均かTOPIXのインデックスで十分</strong><br>攻めるなら日経平均、広く分散ならTOPIX。</li>
      </ol></div>
      <p>大事な注意点を一つ。今日の話は<strong>「もう一歩上を目指す中級者向けの“トッピング”」</strong>です。「管理は面倒」という方は、これまで通り全世界株式1本でまったく問題ありません。それが一番楽で、間違いのない道です。中身を理解し、自分のリスク許容度を確認したうえで、日本株という選択肢も検討してみてください。</p>
"""

write(s4,h4,t4,"老後の資産形成","3,200",lead4,toc4,body4,sn4,d4,k4,"資産形成")
write(s5,h5,t5,"市場解説","2,800",lead5,toc5,body5,sn5,d5,k5,"資産運用")
write(s6,h6,t6,"日本株戦略","3,100",lead6,toc6,body6,sn6,d6,k6,"資産運用")

# ===================== ARTICLE 7: オルカン取り崩しの大誤算
s7="nisa-withdrawal-miscalculation"; h7="blog_nisa_withdrawal_header.webp"
t7="【新NISA出口戦略】50代・60代が「オルカン取り崩し」で直面する3つの大誤算｜年金カット・税金の壁を回避して手取りを最大化する方法"
d7="新NISAでオルカンを積み立ててきたものの、出口戦略がないと老後に大損する可能性があります。定額法・定率法・4%ルールの比較から、2026年最新の年金カット基準緩和（65万円）への対応、健康保険料や医療費などの「所得の壁」をすべて無効化する新NISAの最強の特性を現役FPが解説。"
k7="新NISA 出口戦略, オルカン 取り崩し, 定期売却サービス, 在職老齢年金 2026年, 住民税非課税世帯, 所得の壁"
sn7="新NISA 出口戦略 / オルカン 取り崩し / 定期売却サービス / 在職老齢年金 2026年 / 住民税非課税世帯 / 所得の壁"
lead7=('<p>「新NISAでオルカン（全世界株式）の積立を始めたから、これで老後は安心！」そう思っていませんか？'
       '実は、増やすこと（入口）ばかり考えて<strong>使うこと（出口）を設計していないと、いざ取り崩す時に思わぬ大誤算に直面する</strong>ことになります。'
       '汗水たらして貯めた老後資金をいざ使おうとした瞬間、税金や保険料が跳ね上がったり、年金をカットされたりする罠が待ち受けているのです。'
       'この記事では、50代・60代が絶対に知っておくべき「新NISAの出口戦略」と、あらゆる老後の壁をすり抜ける新NISAの驚くべき強さについて解説します。</p>')
toc7=[("s1","出口設計なし？オルカン取り崩しの「3つの手法」と自動化"),
      ("s2","【2026年最新】年金カット基準が65万円へ引き上げ！新NISAは完全に対象外"),
      ("s3","健康保険料・医療費・非課税世帯…老後の「見えない所得の壁」"),
      ("s4","新NISAは「覆面のお財布」：手取りを最大化する出口戦略の結論"),
      ("s5","まとめ：増やすだけで終わらせない、賢い老後の使い方")]
body7=f"""
      <h2 id="s1">出口設計なし？オルカン取り崩しの「3つの手法」と自動化</h2>
      <p>「オルカンを積み立てて、いざ使う時にどうやって切り崩せばいいのか分からない」——そんな相談を本当によくいただきます。貯める勉強は一生懸命するのに、使う勉強は誰も教えてくれない。これが最初の落とし穴です。</p>
      <p>資産を取り崩す方法には、大きく分けて以下の3つのアプローチがあります。</p>
      
      <table class="comparison-table">
        <thead>
          <tr>
            <th>手法</th>
            <th>やり方</th>
            <th>メリット</th>
            <th>デメリット</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="label">定額法</td>
            <td>毎月決まった金額（例：10万円）を取り崩す</td>
            <td>受取額が一定で生活設計がしやすい</td>
            <td>下落相場でも同じ額を売るため資産枯渇が早まる</td>
          </tr>
          <tr>
            <td class="label">定率法</td>
            <td>残高の決まった割合（例：毎年4%）を取り崩す</td>
            <td>資産が減れば受取額も減るため長持ちする</td>
            <td>相場によって受取額が変動し、予定が立てにくい</td>
          </tr>
          <tr>
            <td class="label">4%ルール</td>
            <td>初年度に4%分を崩し、翌年以降はインフレ率を上乗せ</td>
            <td>理論上30年以上資産が尽きにくい（トリニティスタディ）</td>
            <td>為替の影響を受ける日本人の場合、鵜呑みは危険</td>
          </tr>
        </tbody>
      </table>
      
      <p>実務では、これらを組み合わせる「ハイブリッド手法」が有効です。たとえば、資産が十分にあるうちは「定率」でゆったり増やしながら取り崩し、残高が1,000万円を下回るなど一定のラインに達したら、生活防衛のために「定額」に切り替える。こうすることで、資産寿命を延ばしつつ生活の安定も両立できます。</p>
      
      <div class="info-box">
        <p><strong>💡 SBI証券の最新アップデート</strong><br>
        「毎月自分で売却手続きをするのは面倒」という方のために、証券会社には「定期売却サービス」があります。なんと<strong>SBI証券は2025年12月6日から、NISA口座での定期売却に対応</strong>しました（楽天証券は対応済み）。設定しておけば自動的に売却して口座に現金を振り込んでくれるため、まるで「自分専用の年金」のように受け取れます。ぜひ活用しましょう！</p>
      </div>

      <h2 id="s2">【2026年最新】年金カット基準が65万円へ引き上げ！新NISAは完全に対象外</h2>
      <p>60代以降も元気に働き続ける方が増えていますが、ここで立ちふさがるのが<strong>「在職老齢年金」</strong>という制度です。給料と年金の合計額が基準を超えると、厚生年金がカットされてしまう恐ろしいルールです。</p>
      
{svg_panel("在職老齢年金の基準額改定", [("2025年度までの基準：月51万円","超えた分の半額が年金カットされる"),("2026年4月からの新基準：月65万円","基準が14万円引き上げられ大幅に緩和！")], "#0d1f35","#1a3a5c")}
      
      <p>嬉しいニュースとして、<strong>2026年4月からこの基準額が従来の「51万円」から「65万円」に引き上げられました。</strong>これによって、以前よりも働きながら年金を満額受け取りやすくなっています。</p>
      
      <div class="emphasis-box">
        <p><strong>【計算例】給料45万円、厚生年金25万円の場合（合計70万円）</strong><br>
        ・基準額65万円を超える額：70万円 − 65万円 ＝ 5万円<br>
        ・カットされる額：5万円 ÷ 2 ＝ <strong>毎月2.5万円（年間30万円）</strong>が支給停止されます。<br>
        ※カットされるのは厚生年金だけで、国民年金（基礎年金）はどれだけ稼いでも1円も減らされません。</p>
      </div>
      
      <p>では、この年金カットを回避しつつ、自由に使えるお金を増やすにはどうすればいいでしょうか？</p>
      <p>答えは非常にシンプル。<strong>「新NISAの取り崩し」からお金を出すこと</strong>です。年金カットの判定材料になるのは「働いて得た給料（総報酬月額相当額）」だけ。新NISAをいくら取り崩しても給料とはみなされないため、年金カットの判定には<strong>1円も影響せず、完全にノーカウント</strong>になります。同じ20万円を得るにしても、労働時間を増やして稼ぐと年金が減るのに対し、新NISAから出せば年金は満額のまま手取りだけが増えるのです。</p>

      <h2 id="s3">健康保険料・医療費・非課税世帯…老後の「見えない所得の壁」</h2>
      <p>「年金がカットされないなら、普通に株の特定口座（課税口座）から取り崩してもいいのでは？」と思った方、ここが最大の大誤算ポイントです。老後には、税金や年金だけでなく、<strong>「所得の壁」による様々な負担増加</strong>が待ち受けています。</p>
      
{svg_panel("所得増加でぶつかる老後の3つの壁", [("①健康保険料・介護保険料の壁","所得に応じて毎月の保険料が跳ね上がる"),("②医療費窓口負担の壁（75歳以上）","所得基準を超えると窓口負担が1割から2割・3割へ"),("③住民税非課税世帯の壁","様々な給付や減免措置の恩恵から外れてしまう")], "#1a1020","#3a1a2a", accent="#f5a0a0", rowfill="#3a1820", rowstroke="#a05060", subcol="#d8a0a0")}
      
      <p>課税口座で株を売って得た利益や、iDeCoを年金形式で受け取ったお金は、税法上の「所得」としてカウントされます。所得が増えると、以下の負担が芋づる式に増えていきます。</p>
      <ul>
        <li><strong>社会保険料の増額：</strong>健康保険料や介護保険料は所得に応じて上がります。</li>
        <li><strong>医療費自己負担の増加：</strong>75歳以上の後期高齢者医療制度では、所得が基準を超えると窓口負担割合が1割から2割（または3割）に倍増します。</li>
        <li><strong>住民税非課税世帯の離脱：</strong>非課税世帯（単身で所得45万円以下などが目安）から外れると、高額療養費の上限額が上がり、介護保険の負担割合も増えるなど、大きな不利益が生じます。</li>
      </ul>
      <p>つまり、せっかく資産運用で利益を出して取り崩しても、それを「所得」として申告した瞬間、裏で保険料や医療費としてどんどんお金をむしり取られてしまうわけです。</p>

      <h2 id="s4">新NISAは「覆面のお財布」：手取りを最大化する出口戦略の結論</h2>
      <p>ここで、新NISAの持つ<strong>最大のチート特性</strong>が牙を剥きます。新NISAの口座から取り崩したお金は、どれだけ利益が出ていようが、どれだけ大金を売却しようが<strong>「非課税所得」となり、所得の計算において完全に無視されます。</strong></p>
      
      <div class="emphasis-box">
        <p>新NISAは、役所の目にも税務署の目にも「1円も使っていない（所得ゼロ）」ように見える、いわば<strong>『覆面のお財布』</strong>なのです。</p>
      </div>
      
      <p>いくら取り崩して贅沢な暮らしをしようが、健康保険料は上がらないし、医療費負担割合も1割のまま。住民税非課税世帯の恩恵も維持できます。この強烈なアドバンテージがあるからこそ、50代・60代の出口戦略において、新NISA口座は他のどの口座よりも優先して使う価値があるのです。</p>
      
      <div class="warning-box">
        <p><strong>⚠️ 出口戦略の結論</strong><br>
        ・<strong>課税口座（特定口座）や給料：</strong>これらは所得としてカウントされ、壁に当たります。生活に必要な最低限の所得（非課税世帯枠や年金カット基準以下）に抑えるのが鉄則です。<br>
        ・<strong>新NISA口座の取り崩し：</strong>所得の壁をすり抜けるため、生活費の不足分はここから優先的に補填し、手取りを最大化します。</p>
      </div>
      <p>ただし、一人ひとりの年金額や資産規模、家族構成によって最適な引き出し順序やバランスは異なります。「100人いれば100通りの正解」があるため、まずはご自身の将来の年金見込額や必要生活費を書き出し、具体的な計画を立てていきましょう。</p>

      <h2 id="s5">まとめ：増やすだけで終わらせない、賢い老後の使い方</h2>
      <div class="summary-box">
        <h3>新NISA出口戦略の重要ポイント</h3>
        <ol>
          <li style="margin-bottom:12px;"><strong>取り崩しの仕組みを理解する</strong><br>定額と定率のハイブリッド。SBI証券の定期売却サービスがNISA対応し、完全自動化が可能に。</li>
          <li style="margin-bottom:12px;"><strong>2026年4月の法改正と新NISAの連携</strong><br>在職老齢年金のカット基準が65万円に緩和。新NISAの取り崩しは対象外なので、働きながら満額年金を受け取る強力な味方になります。</li>
          <li><strong>所得の壁を回避する「覆面の財布」</strong><br>新NISAは非課税のため、健康保険料、医療費自己負担、住民税非課税世帯の判定に一切影響しません。老後の手取り最大化には新NISAが最強です。</li>
        </ol>
      </div>
      <p>資産運用は「増やすこと」がゴールではありません。「上手に使って、自分の人生を豊かにすること」こそが本当のゴールです。正しい出口戦略を身につけて、汗水たらして築いた資産を賢く、そして安心して取り崩していきましょう！</p>
"""

# Update date for article 7
DATE_ISO = "2026-06-08"
DATE_JP = "2026年6月8日"
write(s7,h7,t7,"老後の資産形成","3,500",lead7,toc7,body7,sn7,d7,k7,"資産形成")

print("DONE batch2")


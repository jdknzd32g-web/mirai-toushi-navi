import os
import sys
import shutil
import datetime
import re
import argparse
from pathlib import Path
import google.generativeai as genai

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_ROOT = PROJECT_ROOT / "blog"
YEAR_DIR = BLOG_ROOT / "2025"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-K4EG9Q6FL6"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-K4EG9Q6FL6');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 未来投資navi</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="https://eva-solution.netlify.app/blog/2025/{slug}/{slug}.html">

    <!-- OGP -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://eva-solution.netlify.app/blog/2025/{slug}/{slug}.html">
    <meta property="og:title" content="{title} | 未来投資navi">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://eva-solution.netlify.app/blog/2025/{slug}/{image_name}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="675">
    <meta property="og:image:alt" content="{title}">
    <meta property="og:site_name" content="未来投資navi">
    <meta property="article:published_time" content="{date_iso}">
    <meta property="article:author" content="りょう">
    <meta property="article:section" content="{category_label}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@investment_navi">
    <meta name="twitter:creator" content="@investment_navi">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://eva-solution.netlify.app/blog/2025/{slug}/{image_name}">
    <meta name="twitter:image:alt" content="{title}">

    <!-- 構造化データ (JSON-LD) -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title}",
      "description": "{description}",
      "image": "https://eva-solution.netlify.app/blog/2025/{slug}/{image_name}",
      "author": {{
        "@type": "Person",
        "name": "りょう"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "未来投資navi",
        "logo": {{
          "@type": "ImageObject",
          "url": "https://eva-solution.netlify.app/images/logo.png"
        }}
      }},
      "datePublished": "{date_iso}",
      "dateModified": "{date_iso}",
      "mainEntityOfPage": {{
        "@type": "WebPage",
        "@id": "https://eva-solution.netlify.app/blog/2025/{slug}/{slug}.html"
      }}
    }}
    </script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9806798165325885" crossorigin="anonymous"></script>

    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.8; color: #333; background: #f8f9fa; }}
        .header {{ background: white; padding: 15px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 100; }}
        .header-content {{ max-width: 800px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 20px; font-weight: bold; color: #2c3e50; }}
        .back-btn {{ background: #667eea; color: white; padding: 8px 20px; border-radius: 20px; text-decoration: none; font-size: 14px; transition: all 0.3s; }}
        .back-btn:hover {{ background: #5569d0; transform: translateY(-2px); }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; margin-top: 20px; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 2px 20px rgba(0,0,0,0.05); }}
        .article-meta {{ margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .category {{ display: inline-block; background: #4CAF50; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: bold; margin-bottom: 10px; }}
        .date {{ color: #999; font-size: 14px; }}
        h1 {{ font-size: 28px; color: #2c3e50; margin-bottom: 20px; line-height: 1.4; }}
        h2 {{ font-size: 22px; color: #667eea; margin: 40px 0 20px 0; padding-bottom: 10px; border-bottom: 2px solid #667eea; }}
        h3 {{ font-size: 18px; color: #764ba2; margin: 30px 0 15px 0; }}
        p {{ margin-bottom: 20px; line-height: 1.8; }}
        ul, ol {{ margin: 20px 0; padding-left: 30px; }}
        li {{ margin-bottom: 10px; line-height: 1.7; }}
        .highlight {{ background: linear-gradient(transparent 70%, #fff59d 70%); font-weight: bold; padding: 2px 4px; }}
        
        /* Advanced Styles */
        .number-box {{ background: #f0f4ff; border: 2px solid #667eea; border-radius: 10px; padding: 20px; margin: 25px 0; }}
        .number-box h4 {{ color: #667eea; margin-bottom: 15px; font-size: 16px; }}
        .calculation {{ background: #fff; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
        .calculation-highlight {{ background: #e8f5e8; border-left-color: #4CAF50; }}
        .concept-box {{ background: #f8f9fa; border: 2px solid #667eea; border-radius: 10px; padding: 20px; margin: 25px 0; text-align: center; }}
        .concept-box h4 {{ color: #667eea; margin-bottom: 15px; }}

        /* CTA Blocks */
        .youtube-cta {{ background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%); color: white; padding: 20px; border-radius: 10px; margin: 30px 0; text-align: center; }}
        .youtube-cta h3 {{ color: white; margin-top: 0; margin-bottom: 10px; }}
        .youtube-btn {{ background: white; color: #FF0000; padding: 12px 30px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 10px; transition: all 0.3s; }}
        .youtube-btn:hover {{ transform: scale(1.05); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}

        .line-cta {{ background: linear-gradient(135deg, #00C300 0%, #00A000 100%); color: white; padding: 25px; border-radius: 10px; margin: 30px 0; text-align: center; }}
        .line-cta h3 {{ color: white; margin-top: 0; margin-bottom: 15px; }}
        .line-btn {{ background: white; color: #00C300; padding: 14px 35px; border: none; border-radius: 25px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 10px; transition: all 0.3s; }}
        .line-btn:hover {{ transform: scale(1.05); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}

        /* Related Articles */
        .related-articles {{ background: #f8f9fa; padding: 30px; border-radius: 10px; margin-top: 40px; }}
        .related-articles h3 {{ text-align: center; margin-bottom: 20px; color: #333; }}
        .article-card-thumb {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; text-decoration: none; color: inherit; display: block; transition: all 0.3s; border: 1px solid #eee; }}
        .article-card-thumb:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .article-card-thumb h4 {{ color: #667eea; margin-bottom: 8px; font-size: 16px; }}
        .article-card-thumb p {{ color: #666; font-size: 14px; margin: 0; line-height: 1.5; }}

        .footer-cta {{ text-align: center; margin-top: 40px; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; }}
        .footer-cta h3 {{ color: white; margin-bottom: 15px; }}
        .main-cta-btn {{ background: white; color: #667eea; padding: 16px 40px; border: none; border-radius: 30px; font-weight: bold; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 15px; transition: all 0.3s; }}
        .main-cta-btn:hover {{ transform: scale(1.05); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 20px; margin: 10px; }}
            h1 {{ font-size: 24px; }}
            h2 {{ font-size: 20px; }}
            .header-content {{ flex-direction: column; gap: 15px; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">eva solution</div>
            <a href="../../../index.html" class="back-btn">トップページへ戻る</a>
        </div>
    </header>

    <div class="container">
        <!-- Header Image -->
        <div class="article-header-image" style="margin: -40px -40px 30px -40px; border-radius: 12px 12px 0 0; overflow: hidden;">
            <img src="{image_name}" alt="{title}" style="width: 100%; height: auto; display: block;" width="1200" height="675">
        </div>

        <div class="article-meta">
            <span class="category">{category_label}</span>
            <div class="date">{date_display}</div>
        </div>

        <h1>{title}</h1>

        {body_content}

        <div class="footer-cta">
            <h3>もっと詳しい投資情報をお求めの方へ</h3>
            <p>公式LINEでは、個別相談や最新の投資情報を配信中！<br>
            50代・60代に特化した資産形成のヒントをお届けします。</p>
            <a href="../../../index.html" class="main-cta-btn">メインページで詳細を見る</a>
        </div>
    </div>
</body>
</html>
"""

def determine_category(text_path):
    filename = text_path.name.lower()
    content = text_path.read_text(encoding='utf-8').lower()
    
    if 'nisa' in filename or 'nisa' in content:
        return 'nisa-start-guide', '新NISA'
    if any(x in filename or x in content for x in ['fund', 'mutual', 'trust', 'kabu']):
        return 'mutual-fund', '投資信託'
    if any(x in filename or x in content for x in ['life', 'plan', 'retire']):
        return 'life-plan', 'ライフプラン'
    return 'region', '地域別資産運用'

def get_next_slug(category):
    # Find existing slugs in 2025/category*
    # Pattern: category + number
    pattern = re.compile(rf"{category}(\d+)")
    max_num = 0
    
    if not YEAR_DIR.exists():
        return f"{category}1"

    for path in YEAR_DIR.iterdir():
        if path.is_dir() and path.name.startswith(category):
            match = pattern.search(path.name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
    
    return f"{category}{max_num + 1}"

def beautify_text(text):
    """Uses Gemini API to add punctuation and natural flow to the script."""
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Skipping AI beautification.")
        return text

    prompt = f"""
あなたはプロのブログ編集者です。
以下のYouTube台本（テキスト）を、ブログ記事形式にリライトしてください。

【編集ルール】
1. **句読点**: 適切な位置に「、」「。」を入れ、読みやすい日本語にしてください。
2. **装飾**: 記事の中で特に重要な結論や強調したい文言は、`<span class="highlight">`と`</span>`で囲ってください。（例: `<span class="highlight">ここは重要です</span>`）
3. **構成**: 見出し（h2, h3）を適切に配置し、SEOを意識した構成にしてください。
4. **結び**: 記事の最後は必ず「それではまた。」で締めくくってください。
5. **出力形式**: HTMLタグ（h2, h3, p, ul, li, span class="highlight"）を含んだ形式で出力してください。markdown記法（#など）は使用しないでください。
   - タイトル行は `<h1>タイトル</h1>` ではなく、単に `タイトル：〇〇` としてください。
   - 各段落は `<p>` タグで囲ってください。

【重要】「はい」「承知しました」などの返答は一切不要です。記事の本文のみを出力してください。

【台本内容】
{text}
"""
    try:
        model = genai.GenerativeModel('models/gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in AI beautification: {e}")
        return text

def parse_text_content(text_path):
    raw_text = text_path.read_text(encoding='utf-8')
    
    # 0. Beautify with AI
    beautified = beautify_text(raw_text)
    lines = beautified.splitlines()
    
    title = ""
    description = ""
    body_lines = []
    
    # Extract Title
    for i, line in enumerate(lines):
        if line.startswith("タイトル：") or line.startswith("Title:"):
            title = line.split("：")[-1].split(":")[-1].strip()
            continue
        if i == 0 and not title and line.strip():
            title = line.lstrip("#").strip()
            continue
            
        if not body_lines and not line.strip():
            continue
            
        body_lines.append(line)

    # Extract Description
    for line in body_lines:
        clean_line = line.strip()
        if clean_line and not clean_line.startswith(('#', 'OP', '第', '<')):
             description = clean_line[:150] + "..."
             break
    if not description:
        description = title

    # Format Body HTML
    formatted_body = []
    in_list = False
    in_box = False
    in_quote = False  # Track if we are inside smart quotes
    
    has_greeting = any("りょうです" in line or "りょう" in line for line in body_lines[:20])
    if not has_greeting:
        formatted_body.append("<p>こんにちは、りょうです。</p>")

    for line in body_lines:
        line = line.strip()
        if not line:
            if in_list:
                formatted_body.append("</ul>")
                in_list = False
            continue

        if line.startswith("OP：") or line.startswith("ED：") or line.startswith("タイトル"):
            continue

        # Headings
        # Headings
        # Robustly check for H2 (Chapter headers) even if AI added extra #s
        clean_heading = line.lstrip("#").strip()
        is_chapter_h2 = (clean_heading.startswith("第") and "章" in clean_heading) or line.startswith("## ")
        
        if is_chapter_h2:
             # Insert YouTube CTA & Embed BEFORE Chapter 1
             if "第1章" in clean_heading or "1章" in clean_heading:
                 formatted_body.append("""
         <div class="youtube-cta">
            <h3>🎥 YouTubeでもっと詳しく解説！</h3>
            <p>2026年の改正ポイントや、具体的な対策について動画で解説しています。<br>
            「文章だけじゃ不安」という方は、ぜひ動画をご覧ください👇</p>
            <a href="https://www.youtube.com/@investment_navi" target="_blank" class="youtube-btn">
                YouTubeチャンネルを見る
            </a>
        </div>

                 """)

             
             formatted_body.append(f"<h2>{clean_heading}</h2>")
             continue
        
        if line.startswith("### "):
             clean_h3 = line.replace("### ", "").strip()
             formatted_body.append(f"<h3>{clean_h3}</h3>")
             continue

        # Lists
        if line.startswith("・") or line.startswith("- "):
            if not in_list:
                formatted_body.append("<ul>")
                in_list = True
            content = line[1:].strip()
            formatted_body.append(f"<li>{content}</li>")
            continue
        
        if in_list:
            formatted_body.append("</ul>")
            in_list = False

        # Highlight
        line = re.sub(r'\*\*(.+?)\*\*', r'<span class="highlight">\1</span>', line)
        
        # Paragraphs & Smart Line breaks at periods
        # Split by period and join with <br>, BUT ignore periods inside quotes 「...」
        formatted_line = ""
        current_segment = ""
        in_quote = False
        
        for char in line:
            if char == "「":
                in_quote = True
            elif char == "」":
                in_quote = False
            
            current_segment += char
            
            if char == "。" and not in_quote:
                formatted_line += current_segment + "<br>"
                current_segment = ""
        
        formatted_line += current_segment
        
        # Clean up trailing <br>
        if formatted_line.endswith("<br>"):
            formatted_line = formatted_line[:-4]

        formatted_body.append(f"<p>{formatted_line}</p>")

    # Add LINE CTA at the end
    formatted_body.append('<div class="line-cta"><h3>💬「老後資金、どうやって増やせば...？」</h3><p>そんなお悩みにお答えするヒントを、LINEで無料配信中！<br>個別相談も承っています。</p><a href="https://lin.ee/FxIOpk1" target="_blank" class="line-btn">無料LINE登録はこちら</a></div>')

    return title, description, "\n".join(formatted_body)

def update_indexes(slug, title, description, image_name, category_slug, category_label):
    # Update category page
    category_file = BLOG_ROOT / f"category-{category_slug.split('-')[0] if 'nisa' not in category_slug else 'nisa'}.html"
    # Fallback for complex categories mapping
    if 'nisa' in category_slug:
        category_file = BLOG_ROOT / "category-nisa.html"
    elif 'mutual' in category_slug:
        category_file = BLOG_ROOT / "category-mutual-fund.html"
    elif 'life' in category_slug:
        category_file = BLOG_ROOT / "category-life-plan.html"
    else:
        category_file = BLOG_ROOT / "category-region.html"

    if category_file.exists():
        content = category_file.read_text(encoding='utf-8')
        new_card = f"""            <!-- 記事: {slug} -->
            <article class="article-card" onclick="location.href='2025/{slug}/{slug}.html'">
                <div class="article-meta">
                    <span class="article-date">{datetime.date.today().strftime('%Y.%m.%d')}<span class="new-badge">NEW</span></span>
                    <span class="article-level level-beginner">初心者向け</span>
                </div>
                <h2 class="article-title">{title}</h2>
                <p class="article-description">{description}</p>
                <div class="article-tags"><span class="tag">{category_label}</span></div>
                <div class="read-more">続きを読む →</div>
            </article>\n\n"""
        # Insert before first article comment or appropriate marker
        if "<!-- 記事" in content:
            content = re.sub(r"(<!-- 記事)", new_card + r"\1", content, count=1)
        else:
            # Fallback insertion
            pass 
        category_file.write_text(content, encoding='utf-8')
        print(f"Updated {category_file.name}")

    # Update blog/index.html
    index_file = BLOG_ROOT / "index.html"
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        new_card = f"""      <a class="card" href="2025/{slug}/{slug}.html">
        <img class="thumb" src="2025/{slug}/{image_name}" alt="{title}" loading="lazy" decoding="async">
        <div class="card-body">
          <h3 class="card-title">{title}</h3>
          <p class="card-desc">{description}</p>
        </div>
      </a>\n\n"""
        
        # Basic injection strategy - search for category sections
        # This is simplified; ideally we'd parse the HTML structure more robustly
        insertion_point = "<!-- NISA 系（日付降順） -->"
        if 'nisa' not in category_slug:
             insertion_point = "<!-- 投資信託 系 -->" # Default fallback
        
        if insertion_point in content:
             content = content.replace(insertion_point, insertion_point + "\n" + new_card)
        index_file.write_text(content, encoding='utf-8')
        print(f"Updated blog/index.html")

    # Update sitemap.xml
    sitemap_file = PROJECT_ROOT / "sitemap.xml"
    if sitemap_file.exists():
        content = sitemap_file.read_text(encoding='utf-8')
        new_entry = f"""  <url>
    <loc>https://eva-solution.netlify.app/blog/2025/{slug}/{slug}.html</loc>
    <lastmod>{datetime.date.today().isoformat()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <image:image>
      <image:loc>https://eva-solution.netlify.app/blog/2025/{slug}/{image_name}</image:loc>
      <image:title>{title}</image:title>
    </image:image>
  </url>\n"""
        content = content.replace('</urlset>', new_entry + '</urlset>')
        sitemap_file.write_text(content, encoding='utf-8')
        print(f"Updated sitemap.xml")

def generate_thumbnail_image(slug, title, output_path):
    """Generates a YouTube thumbnail-style image using Gemini."""
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Cannot generate thumbnail.")
        # Create empty placeholder
        output_path.touch()
        return

    ref_image_path = PROJECT_ROOT / "images" / "りょう（未来投資navi）.png"
    
    # Text overlay logic: Use Short Catchy Phrase (max ~15 chars)
    # Clean up title just in case (remove markdown headers if leaked)
    clean_title = title.replace("##", "").strip()
    
    # Extract catchy phrase strategy:
    # 1. Split by delimiters like ？, ！, ： and take the LAST part if meaningful, or FIRST part if it's the main topic.
    # 2. Prefer shorter segments for better visibility.
    delimiters = ["？", "！", "：", " ", "　"]
    catchy_text = clean_title
    
    # Try splitting by '：' or '？' first (common in YouTube titles)
    if "：" in clean_title:
        parts = clean_title.split("：")
        catchy_text = parts[-1] if len(parts[-1]) > 3 else parts[0]
    elif "？" in clean_title:
         # "2026年...投資すべき？" -> "投資すべき？"
         parts = clean_title.split("？")
         if len(parts[0]) < 20: # If the first part is reasonable
             catchy_text = parts[0] + "？"
         else:
             catchy_text = clean_title[:15] # Fallback truncate
    
    # Final safety truncate
    if len(catchy_text) > 15:
        catchy_text = catchy_text[:15]

    prompt = f"""
あなたは最高品質のAI画像生成モデルです。
添付された画像（りょう）を元に、ブログのヘッダー画像を生成してください。

【デザイン要件】
- スタイル: 高品質なアニメ調。YouTubeのサムネイルのように、クリックしたくなるようなインパクトのある構成。
- キャラクター: 添付画像の男性（りょう：眼鏡をかけた誠実な日本人の若者）を、自信に満ちた表情で中央または左右に配置。
- テキスト: 画像内に大きく、太文字で「{catchy_text}」という日本語の文字を入れてください。
  - 重要1: **Japanese Kanji (日本の漢字)**、**Standard Japanese Gothic font (標準的な日本語ゴシック体)**を使用すること。
  - 重要2: 決して**Chinese characters (中国語の漢字・簡体字)**を使用しないこと。違和感のない正しい日本語を描画してください。
  - 重要3: フォントスタイルは**Gothic (ゴシック体)**とし、太く、視認性を最優先してください。背景に埋もれないよう、白抜きや強いアウトライン（縁取り）を適用してください。
- 背景: 「{clean_title}」というテーマに沿った、明るくエネルギッシュな背景（上昇チャート、金貨、デジタル資産など）。
- アスペクト比: **16:9** (1200x675px相当)。

視覚的に非常に強力な、プロフェッショナルなサムネイル画像を生成してください。
画像データのみ（inline_data）を出力してください。
"""

    try:
        print(f"🎨 Generating thumbnail for: {title}...")
        model = genai.GenerativeModel('models/gemini-2.5-flash-image')
        
        img_input = []
        if ref_image_path.exists():
            img_data = ref_image_path.read_bytes()
            img_input = [prompt, {"mime_type": "image/png", "data": img_data}]
        else:
            img_input = [prompt]
            
        response = model.generate_content(img_input)
        
        image_saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✅ Thumbnail saved to {output_path}")
                image_saved = True
                break
                
        if not image_saved:
            print("❌ No image data in response. Using placeholder.")
            output_path.touch()

    except Exception as e:
        print(f"❌ Error generating thumbnail: {e}")
        output_path.touch()

def push_to_github(commit_message):
    try:
        print("🚀 Pushing to GitHub...")
        subprocess.run(["git", "add", "."], check=True, cwd=PROJECT_ROOT)
        subprocess.run(["git", "commit", "-m", commit_message], check=True, cwd=PROJECT_ROOT)
        subprocess.run(["git", "push"], check=True, cwd=PROJECT_ROOT)
        print("✅ Successfully pushed to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Auto Blog Generator")
    parser.add_argument("text_file", help="Path to input text file")
    parser.add_argument("--image", help="Path to header image (optional)")
    parser.add_argument("--push", action="store_true", help="Push to GitHub after generation")
    args = parser.parse_args()

    text_path = Path(args.text_file)
    if not text_path.exists():
        print(f"Error: File {text_path} not found.")
        sys.exit(1)

    print(f"Processing {text_path.name}...")

    # 1. Category & Slug
    cat_slug_base, cat_label = determine_category(text_path)
    slug = get_next_slug(cat_slug_base)
    print(f"Category: {cat_label} ({cat_slug_base})")
    print(f"Slug: {slug}")

    # 2. Directory Creation
    target_dir = YEAR_DIR / slug
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {target_dir}")

    # 3. Content Parsing
    title, description, body_html = parse_text_content(text_path)
    print(f"Title: {title}")

    # 4. Image Handling
    image_name = f"{slug}-image.jpg"
    image_file = target_dir / image_name
    if args.image:
        src_img = Path(args.image)
        if src_img.exists():
            shutil.copy(src_img, image_file)
            print(f"Copied image to {image_file}")
        else:
             print("Provided image not found, generating thumbnail.")
             generate_thumbnail_image(slug, title, image_file)
    else:
        # Generate thumbnail automatically
        generate_thumbnail_image(slug, title, image_file)

    # 5. HTML Generation
    html_content = TEMPLATE_HTML.format(
        title=title,
        description=description,
        slug=slug,
        image_name=image_name,
        date_iso=datetime.date.today().isoformat(),
        date_display=datetime.date.today().strftime('%Y.%m.%d'),
        category_label=cat_label,
        body_content=body_html
    )
    
    (target_dir / f"{slug}.html").write_text(html_content, encoding='utf-8')
    print(f"Generated HTML: {target_dir / f'{slug}.html'}")

    # 6. Update Indexes
    update_indexes(slug, title, description, image_name, cat_slug_base, cat_label)

    # 7. Git Push
    if args.push:
        push_to_github(f"New post: {title} ({slug})")

    print("Done!")

if __name__ == "__main__":
    main()

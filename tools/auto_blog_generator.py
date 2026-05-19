import os
import sys
import shutil
import datetime
import re
import argparse
import subprocess
import random
from pathlib import Path
from PIL import Image
import google.generativeai as genai

sys.path.append("/Users/satoshioka/youtube-project-share/transcription-system/_apps/production")
try:
    from format_script_guardrail import split_long_line_soft
    HAS_GUARDRAIL = True
except ImportError:
    HAS_GUARDRAIL = False

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_ROOT = PROJECT_ROOT / "blog"
POSTS_DIR = BLOG_ROOT / "posts"

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
    <link rel="canonical" href="https://eva-solution.netlify.app/blog/posts/{slug}/{slug}.html">

    <!-- OGP -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://eva-solution.netlify.app/blog/posts/{slug}/{slug}.html">
    <meta property="og:title" content="{title} | 未来投資navi">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://eva-solution.netlify.app/blog/posts/{slug}/{image_name}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="675">
    <meta property="og:image:alt" content="{title}">
    <meta property="og:site_name" content="未来投資navi">
    <meta property="article:published_time" content="{date_iso}">
    <meta property="article:author" content="りょう">
    <meta property="article:tag" content="{category_label}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@investment_navi">
    <meta name="twitter:creator" content="@investment_navi">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://eva-solution.netlify.app/blog/posts/{slug}/{image_name}">
    <meta name="twitter:image:alt" content="{title}">

    <!-- 構造化データ (JSON-LD) -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title}",
      "description": "{description}",
      "image": "https://eva-solution.netlify.app/blog/posts/{slug}/{image_name}",
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
        "@id": "https://eva-solution.netlify.app/blog/posts/{slug}/{slug}.html"
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
        
        .video-container {{ position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px; margin-bottom: 20px; }}
        .video-container iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
        
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
        return 'nisa', '新NISA'
    if any(x in filename or x in content for x in ['fund', 'mutual', 'trust', 'kabu']):
        return 'mutual-fund', '投資信託'
    if any(x in filename or x in content for x in ['life', 'plan', 'retire']):
        return 'life-plan', 'ライフプラン'
    return 'asset', '資産運用'

def get_next_slug(category):
    # すべて posts/ ディレクトリの中に保存する
    pattern = re.compile(rf"{category}(\d+)")
    max_num = 0
    
    if not POSTS_DIR.exists():
        return f"{category}1"

    for path in POSTS_DIR.iterdir():
        if path.is_dir() and path.name.startswith(category):
            match = pattern.search(path.name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
    
    return f"{category}{max_num + 1}"

def generate_seo_description(raw_text, title):
    if not GEMINI_API_KEY:
        return title[:120]
    prompt = f"""以下のブログ記事の本文とタイトルから、検索エンジン（SEO）に最適化されたメタディスクリプション（100文字〜120文字）を作成してください。
ターゲットキーワード（例：50代、60代、新NISA、老後資金、資産運用など、記事内容に合ったもの）を自然に含め、クリックしたくなる魅力的な要約にしてください。
「こんにちは」などの挨拶は不要です。説明文のみ出力してください。

【タイトル】
{title}

【本文】
{raw_text[:1500]}"""
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(prompt)
        desc = response.text.strip().replace("\n", "")
        if len(desc) > 130:
            desc = desc[:127] + "..."
        return desc
    except Exception as e:
        print(f"Warning: Failed to generate SEO description: {e}")
        return title

def crop_to_16_9(image_path):
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            width, height = img.size
            target_width = width
            target_height = int(width * 9 / 16)
            if height > target_height:
                top = (height - target_height) // 2
                bottom = top + target_height
                img_cropped = img.crop((0, top, width, bottom))
                img_cropped.save(image_path)
    except Exception as e:
        print(f"Warning: Failed to crop image to 16:9: {e}")

def generate_section_image(heading_text, output_path):
    if not GEMINI_API_KEY:
        return
    if output_path.exists():
        return
    clean_heading = heading_text.replace("##", "").replace("###", "").strip()
    prompt = f"""対象となる文章: 「{clean_heading}」

・アスペクト比：16:9
・高品質な実写の写真風の画像を出力（アニメやイラストは不可）
・画像内に文字（テキスト、数字、記号）は絶対に含めないこと
・文章を集約してキーワードをまとめる
・まとめたキーワードのイメージ画像を作る"""
    try:
        print(f"🎨 Generating section image for: {clean_heading}...")
        model = genai.GenerativeModel('models/gemini-2.5-flash-image')
        img_input = [prompt]
        response = model.generate_content(img_input)
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                crop_to_16_9(output_path)
                print(f"✅ Section image saved and cropped to 16:9 at {output_path}")
                break
    except Exception as e:
        print(f"❌ Failed to generate section image: {e}")

def parse_text_content(text_path, slug, post_dir):
    raw_text = text_path.read_text(encoding='utf-8')
    
    title = ""
    for line in raw_text.splitlines():
        if "タイトル：" in line or "タイトル:" in line:
            title = line.split("：")[-1].split(":")[-1].strip()
            break
        elif line.startswith("# ") and not title:
            title = line.lstrip("# ").strip()
            break
            
    # EDやエンディングという見出しを「まとめ」に自動変換
    # Using simple replace for simplicity instead of regex
    raw_text = re.sub(r'^##\s*(ED|エンディング|ＥＤ).*$', '## まとめ', raw_text, flags=re.MULTILINE | re.IGNORECASE)
    
    print("🤖 Generating SEO Meta Description...")
    description = generate_seo_description(raw_text, title)

    formatted_body = []
    blocks = re.split(r'\n\s*\n', raw_text.strip())
    
    h2_count = 0
    h3_count = 0
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        if "OP：" in block or "OP:" in block or "タイトル：" in block or "タイトル:" in block:
            continue
            
        if block.startswith("# ") and title in block:
            continue
            
        if block.startswith("## "):
            clean_heading = block.lstrip("#").strip()
            
            # 全記事共通：最初のH2見出しの直前（OPの下）にYouTubeリンクを挿入
            if h2_count == 0:
                formatted_body.append("""
        <div class="youtube-cta">
            <h3>🎥 YouTubeもやってます♪</h3>
            <p>文字だけじゃ伝えきれない話は、動画でゆっくり解説してます〜<br>
            よかったら覗いてみてください👇</p>
            <a href="https://www.youtube.com/channel/UCb-u1hcuQyo7qruBhuiOBZg" target="_blank" class="youtube-btn">
                未来投資naviを見てみる
            </a>
        </div>""")
            
            h2_count += 1
            img_path = post_dir / f"{slug}-h2-{h2_count}.jpg"
            if not img_path.exists():
                generate_section_image(clean_heading, img_path)
            
            formatted_body.append(f"<h2>{clean_heading}</h2>")
            if img_path.exists():
                formatted_body.append(f'<div class="article-sub-image"><img src="{slug}-h2-{h2_count}.jpg" alt="{clean_heading}" style="width: 100%; height: auto; display: block;" width="1200" height="675"></div>')
            continue
            
        if block.startswith("### "):
            clean_h3 = block.lstrip("#").strip()
            formatted_body.append(f"<h3>{clean_h3}</h3>")
            continue
            
        block = block.replace("<ul>", "").replace("</ul>", "").replace("<li>", "").replace("</li>", "")
        html_block = block.replace('\n', '<br>\n')
        
        # 1. 句読点の後に改行がなければ <br> を挿入
        html_block = re.sub(r'([、。！？!?])(?!<br>|\n|」|』|）|\)|</)', r'\1<br>\n', html_block)
        
        # 2. 25文字以上の長文をテキストフォーマットロジックで自然に分割
        if HAS_GUARDRAIL:
            parts = html_block.split('<br>\n')
            new_parts = []
            for part in parts:
                # 余計な空白を取り除きつつ分割
                broken = split_long_line_soft(part)
                new_parts.extend(broken)
            html_block = '<br>\n'.join(new_parts)
        
        # 3. Markdown強調の変換（改行で分断されていても処理できるようDOTALL指定）
        html_block = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_block, flags=re.DOTALL)
        html_block = re.sub(r'==(.*?)==', r'<strong class="highlight">\1</strong>', html_block, flags=re.DOTALL)
        
        # 不要な末尾の <br>\n を削除（pタグ直前の余分な改行を防ぐ）
        html_block = re.sub(r'<br>\n\s*$', '', html_block)
        
        formatted_body.append(f"<p>\n{html_block}\n</p>")

    formatted_body.append('<div class="line-cta"><h3>💬「老後資金、どうやって増やせば...？」</h3><p>そんなお悩みにお答えするヒントを、LINEで無料配信中！<br>個別相談も承っています。</p><a href="https://lin.ee/FxIOpk1" target="_blank" class="line-btn">無料LINE登録はこちら</a></div>')

    final_body = "\n".join(formatted_body).replace("`", "")
    
    return title, description, final_body

def update_sitemap(slug, title, image_name):
    sitemap_file = PROJECT_ROOT / "sitemap.xml"
    if sitemap_file.exists():
        content = sitemap_file.read_text(encoding='utf-8')
        new_entry = f"""  <url>
    <loc>https://eva-solution.netlify.app/blog/posts/{slug}/{slug}.html</loc>
    <lastmod>{datetime.date.today().isoformat()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <image:image>
      <image:loc>https://eva-solution.netlify.app/blog/posts/{slug}/{image_name}</image:loc>
      <image:title>{title}</image:title>
    </image:image>
  </url>\n"""
        if '</urlset>' in content:
            content = content.replace('</urlset>', new_entry + '</urlset>')
            sitemap_file.write_text(content, encoding='utf-8')
            print(f"Updated sitemap.xml")

def generate_thumbnail_image(slug, title, output_path):
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Cannot generate thumbnail.")
        output_path.touch()
        return

    clean_title = title.replace("##", "").strip()
    
    prompt = f"""対象となる文章: 「{clean_title}」

・アスペクト比：16:9
・高品質な実写の写真風の画像を出力（アニメやイラストは不可）
・画像内に文字（テキスト、数字、記号）は絶対に含めないこと
・文章を集約してキーワードをまとめる
・まとめたキーワードのイメージ画像を作る"""
    if output_path.exists():
        print(f"ℹ️ Thumbnail already exists at {output_path}. Skipping generation to preserve it.")
        return
        
    try:
        print(f"🎨 Generating thumbnail for: {title}...")
        model = genai.GenerativeModel('models/gemini-2.5-flash-image')
        
        img_input = [prompt]
            
        response = model.generate_content(img_input)
        
        image_saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                crop_to_16_9(output_path)
                print(f"✅ Thumbnail saved and cropped to 16:9 at {output_path}")
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
    parser.add_argument("--category", choices=['nisa', 'mutual-fund', 'life-plan', 'region'], help="Force category (optional)")
    args = parser.parse_args()

    text_path = Path(args.text_file)
    if not text_path.exists():
        print(f"Error: File {text_path} not found.")
        sys.exit(1)

    print(f"Processing {text_path.name}...")

    if args.category:
        category_map = {
            'nisa': ('nisa', '新NISA'),
            'mutual-fund': ('mutual-fund', '投資信託'),
            'life-plan': ('life-plan', 'ライフプラン'),
            'region': ('region', '資産運用')
        }
        cat_slug_base, cat_label = category_map[args.category]
    else:
        cat_slug_base, cat_label = determine_category(text_path)
    
    if text_path.resolve().parent.parent == POSTS_DIR.resolve():
        slug = text_path.parent.name
        print(f"File is already in {slug}, overwriting it instead of creating a new folder.")
    else:
        slug = get_next_slug(cat_slug_base)
        
    print(f"Category: {cat_label} ({cat_slug_base})")
    print(f"Slug: {slug}")

    target_dir = POSTS_DIR / slug
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {target_dir}")

    title, description, body_html = parse_text_content(text_path, slug, target_dir)
    print(f"Title: {title}")

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
        generate_thumbnail_image(slug, title, image_file)

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

    update_sitemap(slug, title, image_name)

    if args.push:
        push_to_github(f"New post: {title} ({slug})")

    print("Done! 🎉")

if __name__ == "__main__":
    main()

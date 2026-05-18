import re

with open("tools/auto_blog_generator.py", "r") as f:
    content = f.read()

# We want to replace from 'def beautify_text(text):' up to 'def update_sitemap'
start_idx = content.find('def beautify_text(text):')
end_idx = content.find('def update_sitemap(slug, title, image_name):')

new_chunk = """def generate_seo_description(raw_text, title):
    if not GEMINI_API_KEY:
        return title[:120]
    prompt = f\"\"\"以下のブログ記事の本文とタイトルから、検索エンジン（SEO）に最適化されたメタディスクリプション（100文字〜120文字）を作成してください。
ターゲットキーワード（例：50代、60代、新NISA、老後資金、資産運用など、記事内容に合ったもの）を自然に含め、クリックしたくなる魅力的な要約にしてください。
「こんにちは」などの挨拶は不要です。説明文のみ出力してください。

【タイトル】
{title}

【本文】
{raw_text[:1500]}\"\"\"
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(prompt)
        desc = response.text.strip().replace("\\n", "")
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
    prompt = f\"\"\"対象となる文章: 「{clean_heading}」

・アスペクト比：16:9
・高品質な実写の写真風の画像を出力（アニメやイラストは不可）
・画像内に文字（テキスト、数字、記号）は絶対に含めないこと
・文章を集約してキーワードをまとめる
・まとめたキーワードのイメージ画像を作る\"\"\"
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
    blocks = re.split(r'\\n\\s*\\n', raw_text.strip())
    
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
            if "第1章" in block or "1章" in block:
                formatted_body.append(\"\"\"
        <div class="video-container">
            <iframe 
                src="https://www.youtube.com/embed/4hVf9QpjD2U?si=5EAeCsvmmtP-N1jH" 
                title="YouTube video player" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                referrerpolicy="strict-origin-when-cross-origin" 
                allowfullscreen>
            </iframe>
        </div>

        <div class="youtube-cta">
            <h3>🎥 YouTubeもやってます♪</h3>
            <p>文字だけじゃ伝えきれない話は、動画でゆっくり解説してます〜<br>
            よかったら覗いてみてください👇</p>
            <a href="https://www.youtube.com/@investment_navi" target="_blank" class="youtube-btn">
                未来投資naviを見てみる
            </a>
        </div>\"\"\")
            
            h2_count += 1
            img_path = post_dir / f"{slug}-h2-{h2_count}.jpg"
            if not img_path.exists():
                generate_section_image(clean_heading, img_path)
            if img_path.exists():
                formatted_body.append(f'<div class="article-sub-image"><img src="{slug}-h2-{h2_count}.jpg" alt="{clean_heading}" style="width: 100%; height: auto; display: block;" width="1200" height="675"></div>')
            formatted_body.append(f"<h2>{clean_heading}</h2>")
            continue
            
        if block.startswith("### "):
            clean_h3 = block.lstrip("#").strip()
            h3_count += 1
            img_path = post_dir / f"{slug}-h3-{h3_count}.jpg"
            if not img_path.exists():
                generate_section_image(clean_h3, img_path)
            if img_path.exists():
                formatted_body.append(f'<div class="article-sub-image"><img src="{slug}-h3-{h3_count}.jpg" alt="{clean_h3}" style="width: 100%; height: auto; display: block;" width="1200" height="675"></div>')
            formatted_body.append(f"<h3>{clean_h3}</h3>")
            continue
            
        block = block.replace("<ul>", "").replace("</ul>", "").replace("<li>", "").replace("</li>", "")
        html_block = block.replace('\\n', '<br>\\n')
        
        html_block = re.sub(r'\\*\\*(.*?)\\*\\*', r'<strong>\\1</strong>', html_block)
        html_block = re.sub(r'==(.*?)==', r'<strong class="highlight">\\1</strong>', html_block)
        
        formatted_body.append(f"<p>\\n{html_block}\\n</p>")

    formatted_body.append('<div class="line-cta"><h3>💬「老後資金、どうやって増やせば...？」</h3><p>そんなお悩みにお答えするヒントを、LINEで無料配信中！<br>個別相談も承っています。</p><a href="https://lin.ee/FxIOpk1" target="_blank" class="line-btn">無料LINE登録はこちら</a></div>')

    final_body = "\\n".join(formatted_body).replace("`", "")
    
    return title, description, final_body\n\n"""

final_content = content[:start_idx] + new_chunk + content[end_idx:]

with open("tools/auto_blog_generator.py", "w") as f:
    f.write(final_content)

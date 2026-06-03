#!/usr/bin/env python3
"""50s-stay-aggressive 記事のヘッダー画像生成（gemini-3-pro-image-preview / 1200x675 / WebP）。
文字・数字・ロゴ・実在UI・人物の顔は出さない編集系ヒーロー写真。
テーマ: 50代が長期の資産形成（新NISA・全世界株式）で前向きに攻める。落ち着いた信頼感、navy×gold。"""
import os, io, sys
from pathlib import Path

OUT = Path("/Users/satoshioka/mirai-toushi-navi/blog/2026/50s-stay-aggressive/blog_50s-stay-aggressive_header.webp")
MODEL = "gemini-3-pro-image-preview"

# .env から API キー読込（プロジェクト .env を優先、無ければホーム .env）
key = None
for env_path in ("/Users/satoshioka/youtube-project-share/.env", "/Users/satoshioka/mirai-toushi-navi/.env", "/Users/satoshioka/.env"):
    p = Path(env_path)
    if not p.exists():
        continue
    for line in p.read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):]
        if line.startswith("GOOGLE_GENERATIVE_AI_API_KEY") or line.startswith("GEMINI_API_KEY"):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if key:
        break
if not key:
    print("[ERROR] API key not found", file=sys.stderr); sys.exit(1)

from google import genai
from google.genai import types
client = genai.Client(api_key=key)

prompt = (
    "Photorealistic editorial photograph, 16:9, calm confident morning light. "
    "Theme: a mature adult in their 50s confidently building long-term wealth, "
    "moving forward with purpose rather than playing only defense. "
    "A refined, well-organized wooden desk scene viewed from above-front: "
    "an open paper notebook with simple hand-drawn ascending growth curves and upward arrows, "
    "a globe or a compass suggesting global diversified investing and a long horizon, "
    "a pocket calculator, a pair of reading glasses, a ceramic coffee cup with gentle steam, "
    "a small healthy green potted plant symbolizing steady growth, and a few neat paper documents. "
    "Shallow depth of field, soft bokeh, cinematic, premium financial-magazine aesthetic, "
    "deep navy and warm gold color accents, trustworthy and forward-looking mood. "
    "IMPORTANT: absolutely no text, no letters, no numbers, no logos, no brand marks, "
    "no smartphone or computer screens or app UI, no human face. Clean, calm and optimistic."
)

resp = client.models.generate_content(
    model=MODEL,
    contents=[types.Part.from_text(text=prompt)],
    config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
)
data = None
for part in resp.candidates[0].content.parts:
    if part.inline_data and part.inline_data.data:
        data = part.inline_data.data; break
if not data:
    txt = " ".join(p.text for p in resp.candidates[0].content.parts if p.text)
    print(f"[ERROR] no image. text={txt[:300]}", file=sys.stderr); sys.exit(2)

from PIL import Image
img = Image.open(io.BytesIO(data)).convert("RGB")
tw, th = 1200, 675
tr, orr = tw/th, img.width/img.height
if orr > tr:
    nh = th; nw = int(img.width*th/img.height)
else:
    nw = tw; nh = int(img.height*tw/img.width)
img = img.resize((nw, nh), Image.LANCZOS)
left, top = (nw-tw)//2, (nh-th)//2
img = img.crop((left, top, left+tw, top+th))
OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "WEBP", quality=82, method=6)
print(f"[OK] saved {OUT} ({OUT.stat().st_size} bytes, {img.width}x{img.height})")

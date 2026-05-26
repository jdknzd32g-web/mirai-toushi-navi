#!/usr/bin/env python3
"""nisa-50s 記事のヘッダー画像生成（gemini-3-pro-image-preview / 1200x675）。
文字・ロゴ・実在UI・人物の顔は出さない編集系ヒーロー写真。"""
import os, io, sys
from pathlib import Path

OUT = Path("/Users/satoshioka/mirai-toushi-navi/blog/2026/nisa-50s/blog_nisa-50s_header.png")
MODEL = "gemini-3-pro-image-preview"

# .env から API キー読込
key = None
for line in Path("/Users/satoshioka/.env").read_text().splitlines():
    if line.startswith("GOOGLE_GENERATIVE_AI_API_KEY"):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")
        break
if not key:
    print("[ERROR] API key not found", file=sys.stderr); sys.exit(1)

from google import genai
from google.genai import types
client = genai.Client(api_key=key)

prompt = (
    "Photorealistic editorial photograph, 16:9, warm hopeful morning light through a window. "
    "A calm, well-organized wooden desk of a mature adult in their 50s planning long-term savings: "
    "an open paper notebook with simple hand-drawn ascending growth curves and arrows, "
    "a pocket calculator, a pair of reading glasses, a ceramic coffee cup with steam, "
    "a small green potted plant, and a few neat paper documents. "
    "Shallow depth of field, soft bokeh, cinematic, premium financial-magazine aesthetic, "
    "navy and warm gold color accents. "
    "IMPORTANT: absolutely no text, no letters, no numbers, no logos, no brand marks, "
    "no smartphone or computer screens or app UI, no human face. Clean and trustworthy mood."
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
img.save(OUT, "PNG")
print(f"[OK] saved {OUT} ({OUT.stat().st_size} bytes)")

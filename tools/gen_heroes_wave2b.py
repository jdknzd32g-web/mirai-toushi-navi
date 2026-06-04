# -*- coding: utf-8 -*-
"""第2波b: asset4 / asset5 / nisa1 のヘッダー写真をGemini画像生成で作成。出力は16:9 WebP。"""
import os, sys
from pathlib import Path

ROOT = Path("/Users/satoshioka/mirai-toushi-navi")
KEY_FILES = [Path("/Users/satoshioka/youtube-project-share/.env"), ROOT / ".env"]
KEY_NAMES = ["GOOGLE_GENERATIVE_AI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]

def _looks_valid(v):
    return v.startswith("AIza") and len(v) >= 35

def find_key():
    candidates = []
    for n in KEY_NAMES:
        v = (os.environ.get(n) or "").strip()
        if v:
            candidates.append((v, f"env:{n}"))
    for f in KEY_FILES:
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            if k.strip() in KEY_NAMES and v:
                candidates.append((v, f"{f}:{k.strip()}"))
    for v, src in candidates:
        if _looks_valid(v):
            return v, src
    return (candidates[0] if candidates else (None, None))

# (posts配下のフォルダ名, ヘッダーファイル名, 生成テーマ)
ARTICLES = [
    ("asset4", "blog_asset4_header.webp",
     "穏やかな朝の光が差し込む書斎の机の上に、観葉植物と小さく芽吹いた若木の鉢、ノートとペン、コーヒーカップが整然と置かれている。成熟した世代が落ち着いて将来設計を始める、前向きで温かい雰囲気の実写風の写真。文字や数字は一切含めない。"),
    ("asset5", "blog_asset5_header.webp",
     "上品なデスクの上で、右肩上がりにゆるやかに上昇していく抽象的なグラフをイメージさせる積み上げられたコインの列と、ぼけた金融市場の背景。冷静さと長期的な安心感を感じさせる、落ち着いた照明の実写風の写真。文字や数字は一切含めない。"),
    ("nisa1", "blog_nisa1_header.webp",
     "木目の落ち着いたテーブルの上に、虫眼鏡と数冊の資料、電卓、メガネが置かれ、慎重に資料を見比べているような構図。商品を見極める冷静さと信頼感を感じさせる、柔らかい自然光の実写風の写真。文字や数字は一切含めない。"),
]

BASE_RULES = """
・アスペクト比：16:9
・高品質な実写の写真風の画像（アニメやイラストは不可）
・画像内に文字（テキスト、数字、記号）は絶対に含めないこと
・落ち着いた信頼感のあるトーン
"""

MAXW = 1280
WEBP_Q = 82

def save_compact_webp(raw_bytes, out_path):
    import io
    from PIL import Image
    out_path = out_path.with_suffix(".webp")
    img = Image.open(io.BytesIO(raw_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    w, h = img.size
    th = int(w * 9 / 16)
    if h > th:
        top = (h - th) // 2
        img = img.crop((0, top, w, top + th))
    if img.width > MAXW:
        img = img.resize((MAXW, round(img.height * MAXW / img.width)), Image.LANCZOS)
    img.save(out_path, "WEBP", quality=WEBP_Q, method=6)
    return out_path

def main():
    key, src = find_key()
    if not key:
        print("ERROR: APIキーが見つかりません")
        sys.exit(2)
    print(f"key source: {src} (len={len(key)})")
    import google.generativeai as genai
    genai.configure(api_key=key)
    model = genai.GenerativeModel("models/gemini-2.5-flash-image")
    ok = 0
    for slug, hero, theme in ARTICLES:
        out = ROOT / "blog/posts" / slug / hero
        prompt = f"対象テーマ: 「{theme}」\n{BASE_RULES}"
        try:
            print(f"generating {slug} ...")
            resp = model.generate_content([prompt])
            saved = False
            for part in resp.candidates[0].content.parts:
                if getattr(part, "inline_data", None):
                    webp = save_compact_webp(part.inline_data.data, out)
                    print(f"saved {webp.name} ({webp.stat().st_size//1024}KB)")
                    saved = True
                    ok += 1
                    break
            if not saved:
                print(f"no image data for {slug}")
        except Exception as e:
            print(f"FAIL {slug}: {e}")
    print(f"DONE: {ok}/{len(ARTICLES)} heroes generated")

if __name__ == "__main__":
    main()

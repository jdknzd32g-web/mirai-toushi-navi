# -*- coding: utf-8 -*-
"""3記事のヘッダー写真をGemini画像生成で作成し、仮置きpngを差し替える。
キーは複数の場所/変数名から自動検出（GOOGLE_GENERATIVE_AI_API_KEY / GEMINI_API_KEY / GOOGLE_API_KEY）。
"""
import os, sys
from pathlib import Path

ROOT = Path("/Users/satoshioka/mirai-toushi-navi")
KEY_FILES = [
    Path("/Users/satoshioka/youtube-project-share/.env"),
    ROOT / ".env",
    Path("/Users/satoshioka/youtube-project-share/.env.example"),
]
KEY_NAMES = ["GOOGLE_GENERATIVE_AI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]

def _looks_valid(v):
    return v.startswith("AIza") and len(v) >= 35

def find_key():
    candidates = []  # (value, source)
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
    # 正規キー(AIza…)を最優先。なければ先頭の候補。
    for v, src in candidates:
        if _looks_valid(v):
            return v, src
    return (candidates[0] if candidates else (None, None))

ARTICLES = [
    ("60s-hands-off-investing", "blog_60s_hands_off_header.png",
     "日本の60代の人が穏やかな表情でコーヒーを片手にくつろぎ、長期のほったらかし投資で安心している様子。窓辺の明るく落ち着いた実写風の写真。お金や数字の文字は含めない。"),
    ("sp500-vs-fang-plus", "blog_sp500_fang_header.png",
     "AIデータセンターと送電インフラ、電力をイメージした近未来的だが落ち着いたトーンの実写風の写真。米国株式市場の二極化とAIインフラ・電力の重要性を象徴する。文字は含めない。"),
    ("japan-stocks-2026", "blog_japan_stocks_2026_header.png",
     "東京の都市と日本のビジネス街を背景に、2026年の日本株への注目を象徴する、落ち着いた品のある実写風の写真。為替と通貨分散のイメージ。文字や数字は含めない。"),
]

BASE_RULES = """
・アスペクト比：16:9
・高品質な実写の写真風の画像（アニメやイラストは不可）
・画像内に文字（テキスト、数字、記号）は絶対に含めないこと
・落ち着いた信頼感のあるトーン
"""

def crop_16_9(path):
    from PIL import Image
    with Image.open(path) as img:
        w, h = img.size
        th = int(w * 9 / 16)
        if h > th:
            top = (h - th) // 2
            img.crop((0, top, w, top + th)).save(path)

def main():
    key, src = find_key()
    if not key:
        print("ERROR: APIキーが見つかりません。下記いずれかに設定してください:")
        for f in KEY_FILES:
            print(f"  - {f}  (変数: {', '.join(KEY_NAMES)})")
        sys.exit(2)
    print(f"key source: {src} (len={len(key)})")
    import google.generativeai as genai
    genai.configure(api_key=key)
    model = genai.GenerativeModel("models/gemini-2.5-flash-image")

    ok = 0
    for slug, hero, theme in ARTICLES:
        out = ROOT / "blog/2026" / slug / hero
        prompt = f"対象テーマ: 「{theme}」\n{BASE_RULES}"
        try:
            print(f"🎨 generating {slug} ...")
            resp = model.generate_content([prompt])
            saved = False
            for part in resp.candidates[0].content.parts:
                if getattr(part, "inline_data", None):
                    out.write_bytes(part.inline_data.data)
                    crop_16_9(out)
                    print(f"✅ saved {out.name}")
                    saved = True
                    ok += 1
                    break
            if not saved:
                print(f"⚠️  no image data for {slug}; placeholder kept")
        except Exception as e:
            print(f"❌ {slug}: {e}; placeholder kept")
    print(f"DONE: {ok}/{len(ARTICLES)} heroes generated")

if __name__ == "__main__":
    main()

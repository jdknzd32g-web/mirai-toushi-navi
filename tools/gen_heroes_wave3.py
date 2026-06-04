# -*- coding: utf-8 -*-
"""第3波: nisa2 / nisa3 / nisa5 のヘッダー写真をGemini画像生成で作成。出力は16:9 WebP。"""
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
    ("nisa2", "blog_nisa2_header.webp",
     "落ち着いた木目のテーブルの上に、貯金箱と数枚のコイン、そして世界地図をうっすら背景にした地球儀、ノートとペンが整然と置かれている。銀行預金だけに頼らず世界へ分散していくイメージの、温かく前向きな実写風の写真。文字や数字は一切含めない。"),
    ("nisa3", "blog_nisa3_header.webp",
     "上品なデスクの上に、株式・債券・金（ゴールド）を象徴するように、積み上げられたコインの三つの山と小さな金塊、落ち着いた色合いの資料が整然と並んでいる。資産のバランスと守りを感じさせる、柔らかな自然光の実写風の写真。文字や数字は一切含めない。"),
    ("nisa5", "blog_nisa5_header.webp",
     "朝日が差し込む窓辺の机の上に、アジアの新興国を象徴する若々しい観葉植物と芽吹いた若木の鉢、半導体チップを思わせる小さな電子部品、ノートが置かれている。成長と未来への期待を感じさせる、明るく前向きな実写風の写真。文字や数字は一切含めない。"),
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

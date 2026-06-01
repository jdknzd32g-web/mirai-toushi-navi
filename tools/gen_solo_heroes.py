# -*- coding: utf-8 -*-
"""記事のヘッダー写真をGemini画像生成で作成する。
出力は必ず軽量WebP（16:9・最大幅1280px・q82、1枚あたり概ね40〜90KB）。
※HTMLのimg src / og:image / sitemapはすべて .webp で参照すること（.pngではない）。
キーは複数の場所/変数名から自動検出（GOOGLE_GENERATIVE_AI_API_KEY / GEMINI_API_KEY / GOOGLE_API_KEY）。
既存画像の一括最適化は tools/optimize_blog_images.py を使う。
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

# (slug, ヘッダーファイル名, 生成テーマ)  ※拡張子は何でも内部で.webpに強制される
ARTICLES = [
    ("silver-2026", "blog_silver-2026_header.webp",
     "磨かれた銀の延べ棒（シルバーインゴット）と銀貨が、濃いグレーの石のテーブルの上に整然と積み重ねられている。背景は柔らかくぼけた金融市場のイメージで、上品で落ち着いた照明。貴金属投資の高級感と緊張感が伝わる実写風の写真。文字や数字は一切含めない。"),
]

BASE_RULES = """
・アスペクト比：16:9
・高品質な実写の写真風の画像（アニメやイラストは不可）
・画像内に文字（テキスト、数字、記号）は絶対に含めないこと
・落ち着いた信頼感のあるトーン
"""

# 出力はコンパクトなWebP固定（写真PNGは重いため）。表示は720px幅コンテナなので最大1280pxで十分。
MAXW = 1280
WEBP_Q = 82

def save_compact_webp(raw_bytes, out_path):
    """Geminiの生成バイトを 16:9クロップ→最大幅1280→WebP(q82) で保存。out_pathの拡張子は.webpに強制。"""
    import io
    from PIL import Image
    out_path = out_path.with_suffix(".webp")
    img = Image.open(io.BytesIO(raw_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    w, h = img.size
    th = int(w * 9 / 16)
    if h > th:                       # 16:9に中央クロップ
        top = (h - th) // 2
        img = img.crop((0, top, w, top + th))
    if img.width > MAXW:             # 最大幅にダウンスケール（拡大はしない）
        img = img.resize((MAXW, round(img.height * MAXW / img.width)), Image.LANCZOS)
    img.save(out_path, "WEBP", quality=WEBP_Q, method=6)
    return out_path

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
                    webp = save_compact_webp(part.inline_data.data, out)
                    print(f"✅ saved {webp.name} ({webp.stat().st_size//1024}KB)  ※HTML/sitemapは.webpで参照")
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

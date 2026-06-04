# -*- coding: utf-8 -*-
"""最終波: blog/2026 内 mutual-fund2 / nisa-start-guide1 / nisa-start-guide2 のヘッダー写真を生成。16:9 WebP。"""
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

# (フォルダ(2026配下), ヘッダーファイル名, 生成テーマ)
ARTICLES = [
    ("mutual-fund2", "blog_mutual_fund2_header.webp",
     "落ち着いた木目のデスクの上に、ノートとペン、コーヒーカップ、観葉植物、そして淡く右肩上がりを思わせる折れ線を描いた紙が静かに置かれている。焦らず長期で資産形成に向き合う、穏やかで前向きな実写風の写真。文字や数字は一切含めない。"),
    ("nisa-start-guide1", "blog_nisa_start_guide1_header.webp",
     "上品なテーブルの上に、株式・債券・金（ゴールド）の分散を象徴するように、積み上げたコインの山と小さな金塊、落ち着いた色合いの資料、万年筆が整然と並んでいる。年初にまとまった資金を計画的に配分する、堅実で落ち着いた雰囲気の実写風の写真。文字や数字は一切含めない。"),
    ("nisa-start-guide2", "blog_nisa_start_guide2_header.webp",
     "朝靄のかかった窓辺の机の上に、コンパスと地図、ノート、そして揺れる天秤の小さな置物が置かれている。先の見えない相場でも冷静に方向を見定める思考を感じさせる、静かで知的な実写風の写真。文字や数字は一切含めない。"),
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
        out = ROOT / "blog/2026" / slug / hero
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

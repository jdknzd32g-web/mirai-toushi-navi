# -*- coding: utf-8 -*-
"""market-crash-dont-sell 記事のヘッダー写真を nanobanana(Gemini) で生成。16:9 WebP。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from gen_solo_heroes import find_key, save_compact_webp, BASE_RULES, ROOT

ARTICLES = [
    ("market-crash-dont-sell", "blog_market_crash_header.webp",
     "嵐の海の上を進む大型タンカー船を遠景で捉えた、荘厳で落ち着いた実写風の写真。暗い雲と高い波が緊張感を表すが、船はどっしりと安定して航行しており、長期投資家の冷静さと不屈を象徴する。色調は深い紺色とグレーを基調に、地平線にわずかな光が差し込む。原油・エネルギー・世界経済の大動脈を連想させる重厚な雰囲気。文字や数字、ロゴは一切含めない。"),
]

def main():
    key, src = find_key()
    if not key:
        print("ERROR: APIキーが見つかりません"); sys.exit(2)
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
            for part in resp.candidates[0].content.parts:
                if getattr(part, "inline_data", None):
                    webp = save_compact_webp(part.inline_data.data, out)
                    print(f"✅ saved {webp.name} ({webp.stat().st_size//1024}KB)")
                    ok += 1
                    break
            else:
                print(f"⚠️  no image data for {slug}")
        except Exception as e:
            print(f"❌ {slug}: {e}")
    print(f"DONE: {ok}/{len(ARTICLES)}")

if __name__ == "__main__":
    main()

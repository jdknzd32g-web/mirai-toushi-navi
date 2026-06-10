# -*- coding: utf-8 -*-
"""retirement-money-investment 記事のヘッダー写真を nanobanana(Gemini) で生成。16:9 WebP。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from gen_solo_heroes import find_key, save_compact_webp, BASE_RULES, ROOT

ARTICLES = [
    ("retirement-money-investment", "blog_retirement_money_header.webp",
     "日本の落ち着いた自宅のリビングで、60代の夫婦が木製のテーブルに向かい、通帳や書類を広げて退職金の使い道を真剣に、しかし穏やかに話し合っている実写風の写真。窓から柔らかな自然光が差し込み、温かみのある安心感のある雰囲気。テーブルには電卓と数枚の書類、湯のみ。背景は上品でぼけている。落ち着いた紺色とベージュを基調にした信頼感のあるトーン。文字や数字、ロゴ、グラフは一切含めない。"),
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
            print(f"generating {slug} ...")
            resp = model.generate_content([prompt])
            for part in resp.candidates[0].content.parts:
                if getattr(part, "inline_data", None):
                    webp = save_compact_webp(part.inline_data.data, out)
                    print(f"saved {webp.name} ({webp.stat().st_size//1024}KB)")
                    ok += 1
                    break
            else:
                print(f"no image data for {slug}")
        except Exception as e:
            print(f"ERROR {slug}: {e}")
    print(f"DONE: {ok}/{len(ARTICLES)}")

if __name__ == "__main__":
    main()

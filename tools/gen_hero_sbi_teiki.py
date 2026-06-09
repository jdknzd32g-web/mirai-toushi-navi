# -*- coding: utf-8 -*-
"""sbi-teiki-baikyaku 記事のヘッダー写真を nanobanana(Gemini) で生成。16:9 WebP。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from gen_solo_heroes import find_key, save_compact_webp, BASE_RULES, ROOT

ARTICLES = [
    ("sbi-teiki-baikyaku", "blog_sbi_teiki_baikyaku_header.webp",
     "明るく落ち着いた日本の住まいのダイニングテーブルに、コーヒーカップ、老眼鏡、ノートと電卓が置かれ、窓から柔らかな朝の光が差し込んでいる。穏やかでゆとりのある退職後の生活と、計画的にお金を受け取る安心感を象徴する、温かく上品な実写風の写真。人物の顔は写さない。文字や数字、ロゴは一切含めない。"),
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

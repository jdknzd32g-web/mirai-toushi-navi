# -*- coding: utf-8 -*-
"""ブログ画像の容量最適化（一括）。
1) プロフィール画像(blog_profile_ryo.jpg)を 144x144 にリサイズ（.jpgのまま=HTML変更不要）
2) 250KB超の写真系ラスター(PNG/JPG)を WebP化（最大幅1280・q82）、元ファイル削除
3) blog配下の全HTML と sitemap.xml の参照(basename)を .png/.jpg -> .webp に一括置換
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path("/Users/satoshioka/mirai-toushi-navi")
BLOG = ROOT / "blog"
MAXW = 1280
WEBP_Q = 82
SIZE_THRESHOLD = 256 * 1024
PROFILE_NAME = "blog_profile_ryo.jpg"
PROFILE_PX = 144

def human(n): return f"{n/1024:.0f}KB"

def resize_profiles():
    saved = 0
    for p in BLOG.rglob(PROFILE_NAME):
        before = p.stat().st_size
        with Image.open(p) as im:
            im = im.convert("RGB")
            im = ImageOps.fit(im, (PROFILE_PX, PROFILE_PX), Image.LANCZOS)
            im.save(p, "JPEG", quality=85, optimize=True)
        after = p.stat().st_size
        saved += before - after
        print(f"  profile {p.relative_to(ROOT)}: {human(before)} -> {human(after)}")
    return saved

def convert_to_webp():
    """戻り値: (old_basename -> new_basename) の置換マップ, 削減バイト"""
    mapping = {}
    saved = 0
    targets = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        for p in BLOG.rglob(ext):
            if p.name == PROFILE_NAME:
                continue
            if p.stat().st_size > SIZE_THRESHOLD:
                targets.append(p)
    for p in sorted(targets, key=lambda x: -x.stat().st_size):
        before = p.stat().st_size
        out = p.with_suffix(".webp")
        with Image.open(p) as im:
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "A" in im.mode else "RGB")
            w, h = im.size
            if w > MAXW:
                im = im.resize((MAXW, round(h * MAXW / w)), Image.LANCZOS)
            im.save(out, "WEBP", quality=WEBP_Q, method=6)
        after = out.stat().st_size
        saved += before - after
        mapping[p.name] = out.name
        p.unlink()
        print(f"  webp {p.relative_to(ROOT)}: {human(before)} -> {out.name} {human(after)}")
    return mapping, saved

def rewrite_refs(mapping):
    if not mapping:
        return 0
    files = list(BLOG.rglob("*.html")) + [ROOT / "sitemap.xml"]
    changed = 0
    for f in files:
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8")
        orig = txt
        for old, new in mapping.items():
            if old in txt:
                txt = txt.replace(old, new)
        # og:image:type / 拡張子由来のMIME（あれば）
        if "blog_" in orig or "-image" in orig or "-hero" in orig:
            txt = txt.replace('content="image/png"', 'content="image/webp"')
            txt = txt.replace('content="image/jpeg"', 'content="image/webp"')
        if txt != orig:
            f.write_text(txt, encoding="utf-8")
            changed += 1
            print(f"  refs updated: {f.relative_to(ROOT)}")
    return changed

def main():
    print("== 1) プロフィール画像リサイズ ==")
    s1 = resize_profiles()
    print("== 2) 写真をWebP化 ==")
    mapping, s2 = convert_to_webp()
    print("== 3) HTML / sitemap 参照更新 ==")
    n = rewrite_refs(mapping)
    print("\n== サマリ ==")
    print(f"  WebP変換: {len(mapping)}枚 / 参照更新: {n}ファイル")
    print(f"  削減合計: {(s1+s2)/1048576:.1f}MB（profile {s1/1048576:.1f}MB + webp {s2/1048576:.1f}MB）")

if __name__ == "__main__":
    main()

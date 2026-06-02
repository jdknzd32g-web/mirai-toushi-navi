#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未来投資navi - YouTube 動画途中挿入用「公式LINE誘導スライド」1枚生成スクリプト
- 背景: nanobanana (Gemini 画像生成 / gemini-3-pro-image = Nano Banana Pro) で生成
- テキスト / QR: Pillow で正確に重ねる（生成AIには文字・QRを一切描かせない）
- 出力: /tmp/line_cta_slide.png (1920x1080 / PNG)

実行: python3 line_cta_slide.py
"""

import os
import sys
import io

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ===========================================================================
# 設定
# ===========================================================================
W, H = 1920, 1080
OUT_PATH = "/tmp/line_cta_slide.png"
QR_PATH = "/Users/satoshioka/youtube-project-share/line-cta-video/line_qr.png"

# nanobanana(Gemini画像生成) モデル候補。先頭から順に試す。
#  - gemini-3-pro-image      : Nano Banana Pro (GA 安定版・高品質)
#  - gemini-3.1-flash-image  : Nano Banana 2 (GA 安定版・高速)
#  - gemini-3-pro-image-preview : 旧プレビュー(2026-06-25 提供終了予定・最後の保険)
MODEL_CANDIDATES = [
    "gemini-3-pro-image",
    "gemini-3.1-flash-image",
    "gemini-3-pro-image-preview",
]

ENV_PATHS = [
    "/Users/satoshioka/.env",
    "/Users/satoshioka/youtube-project-share/.env",
    "/Users/satoshioka/mirai-toushi-navi/.env",
]
ENV_KEY = "GOOGLE_GENERATIVE_AI_API_KEY"

# 日本語フォント候補（W6/W8=太字見出し、W3=本文）。環境差を吸収するため複数 try。
FONT_BOLD_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴ ProN W6.otf",
    "/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
]
FONT_REG_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴ ProN W3.otf",
]

# カラー
WHITE = (255, 255, 255, 255)
GOLD = (212, 175, 105, 255)          # 上品なゴールド
GOLD_SOFT = (224, 196, 140, 255)
LINE_GREEN = (6, 199, 85, 255)       # LINE ブランドグリーン

# 背景生成プロンプト（人物の顔・ロゴ・文字は入れない / 中央〜下部は暗め）
BG_PROMPT = (
    "A calm, warm financial and household-budget consultation atmosphere. "
    "Soft natural window light, a wooden desk with subtle bokeh, a green leafy "
    "houseplant in the corner. Elegant, premium navy-blue and gold color tones. "
    "Cinematic depth of field, photorealistic, high quality. "
    "Composition: keep the center and lower portion darker and uncluttered so that "
    "white overlaid text is highly readable. "
    "Absolutely NO text, NO letters, NO numbers, NO logos, NO watermarks, "
    "NO human faces, NO people. 16:9 widescreen aspect ratio."
)


# ===========================================================================
# ユーティリティ
# ===========================================================================
def load_api_key():
    """ENV_PATHS を順に見て GOOGLE_GENERATIVE_AI_API_KEY を行頭一致で取得。"""
    for path in ENV_PATHS:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s.startswith(ENV_KEY):
                        # KEY=value / KEY: value 両対応
                        _, _, val = s.partition("=")
                        if not val:
                            _, _, val = s.partition(":")
                        val = val.strip().strip('"').strip("'").strip()
                        if val:
                            print(f"[env] API key loaded from {path}")
                            return val
        except Exception as e:
            print(f"[env] read error {path}: {e}", file=sys.stderr)
    # 環境変数フォールバック
    for k in (ENV_KEY, "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        v = os.environ.get(k)
        if v:
            print(f"[env] API key loaded from environment ${k}")
            return v.strip()
    return None


def find_font(candidates, size):
    """候補フォントを順に試し、最初に開けたものを返す。なければデフォルト。"""
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    print("[font] WARNING: 日本語フォントが見つからず default font を使用します。"
          " 日本語が豆腐になる可能性があります。", file=sys.stderr)
    return ImageFont.load_default()


def gen_background(api_key):
    """Gemini(nanobanana)で背景生成。失敗時はグラデーション背景にフォールバック。"""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # 16:9 を image_config で明示（SDK バージョン差を try で吸収）
        cfg_variants = []
        try:
            cfg_variants.append(
                types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    image_config=types.ImageConfig(aspect_ratio="16:9"),
                )
            )
        except Exception:
            pass
        cfg_variants.append(
            types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        )

        last_err = None
        for model in MODEL_CANDIDATES:
            for cfg in cfg_variants:
                try:
                    print(f"[gen] try model={model} ...")
                    resp = client.models.generate_content(
                        model=model,
                        contents=BG_PROMPT,
                        config=cfg,
                    )
                    img_bytes = extract_image_bytes(resp)
                    if img_bytes:
                        print(f"[gen] OK model={model} ({len(img_bytes)} bytes)")
                        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    print(f"[gen] model={model} returned no image, next.")
                except Exception as e:
                    last_err = e
                    print(f"[gen] model={model} failed: {e}", file=sys.stderr)
        print(f"[gen] all models failed. last_err={last_err}", file=sys.stderr)
    except Exception as e:
        print(f"[gen] SDK init failed: {e}", file=sys.stderr)

    print("[gen] フォールバック: グラデーション背景を生成します。")
    return make_fallback_bg()


def extract_image_bytes(resp):
    """resp.candidates[0].content.parts[].inline_data.data から画像bytesを取得。"""
    try:
        cands = getattr(resp, "candidates", None) or []
        for cand in cands:
            content = getattr(cand, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                inline = getattr(part, "inline_data", None)
                if inline is not None and getattr(inline, "data", None):
                    return inline.data
    except Exception as e:
        print(f"[gen] extract error: {e}", file=sys.stderr)
    return None


def make_fallback_bg():
    """ネイビー→ゴールド系の縦グラデ（API 不通時の保険）。"""
    bg = Image.new("RGB", (W, H), (12, 20, 38))
    top = (24, 38, 66)      # 上: ネイビー
    bottom = (8, 12, 24)    # 下: 暗め
    px = bg.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return bg.filter(ImageFilter.GaussianBlur(2))


def cover_resize(img, w, h):
    """16:9 にアスペクト維持で cover クロップ（中央基準）。"""
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    new_w, new_h = int(src_w * scale + 0.5), int(src_h * scale + 0.5)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def text_w(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def draw_center(draw, cy, text, font, fill, shadow=True):
    """水平中央寄せで描画。cy は描画基準 y(top)。戻り値は次行用に使える下端y。"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (W - tw) // 2 - bbox[0]
    y = cy - bbox[1]
    if shadow:
        draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 170))
    draw.text((x, y), text, font=font, fill=fill)
    return cy + th


# ===========================================================================
# メイン
# ===========================================================================
def main():
    api_key = load_api_key()
    if not api_key:
        print("[env] WARNING: API キー未検出。フォールバック背景で続行します。",
              file=sys.stderr)

    # 1) 背景
    bg = gen_background(api_key) if api_key else make_fallback_bg()
    bg = cover_resize(bg, W, H).convert("RGBA")

    # 2) 半透明の暗いオーバーレイ（下部ほど濃く＝白文字が映える）
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(H):
        t = y / (H - 1)
        alpha = int(90 + 110 * t)  # 上 ~90 → 下 ~200
        od.line([(0, y), (W, y)], fill=(6, 10, 20, alpha))
    bg = Image.alpha_composite(bg, overlay)

    draw = ImageDraw.Draw(bg)

    # フォント
    f_kicker = find_font(FONT_BOLD_CANDIDATES, 60)   # 上部見出し
    f_title = find_font(FONT_BOLD_CANDIDATES, 92)    # メイン見出し
    f_label = find_font(FONT_BOLD_CANDIDATES, 40)    # 特典ラベル(先着n名様)
    f_body = find_font(FONT_BOLD_CANDIDATES, 58)     # 特典本文
    f_foot = find_font(FONT_BOLD_CANDIDATES, 54)     # 下部誘導
    f_cap = find_font(FONT_REG_CANDIDATES, 30)       # QRキャプション

    # --- 上部見出し ---
    draw_center(draw, 120, "公式LINE 限定特典", f_kicker, GOLD)

    # ゴールドの区切りライン
    line_w = 520
    lx = (W - line_w) // 2
    draw.line([(lx, 210), (lx + line_w, 210)], fill=GOLD, width=3)

    # --- 特典カード（中央やや上〜中央） ---
    # 特典1
    box1_top = 300
    draw_benefit(
        draw, box1_top,
        badge="特典 1",
        label="先着3名様",
        body="30分 無料相談",
        f_label=f_label, f_body=f_body,
    )
    # 特典2
    box2_top = 540
    draw_benefit(
        draw, box2_top,
        badge="特典 2",
        label="先着2名様",
        body="1ヶ月 体験プラン  税込5,000円",
        f_label=f_label, f_body=f_body,
    )

    # --- 下部誘導 ---
    draw_center(draw, 880, "▼ 概要欄の公式LINEから", f_foot, WHITE)

    # 3) QRコードを右下に配置（白い余白付き）
    place_qr(bg, draw, f_cap)

    # 4) 保存（RGB に戻して PNG）
    bg.convert("RGB").save(OUT_PATH, "PNG")
    print(f"[done] saved -> {OUT_PATH} ({W}x{H})")


def draw_benefit(draw, top, badge, label, body, f_label, f_body):
    """特典1行ぶんを中央寄せで描画（バッジ＋ラベル＋本文）。"""
    # 本文（大きく・白）
    draw_center(draw, top + 60, body, f_body, WHITE)
    # ラベル行（ゴールド）: "● 特典1 ｜ 先着3名様"
    head = f"{badge}  ｜  {label}"
    draw_center(draw, top, head, f_label, GOLD_SOFT)


def place_qr(base_img, draw, f_cap):
    """QRを右下に白余白付きで配置し、上に「友だち追加はこちら」キャプション。"""
    qr_side = 320
    pad = 26            # QR 周囲の白余白
    margin_r = 70       # 右マージン
    margin_b = 70       # 下マージン

    card_side = qr_side + pad * 2
    card_x = W - margin_r - card_side
    card_y = H - margin_b - card_side

    # 白カード（角丸風に白矩形）
    card = Image.new("RGBA", (card_side, card_side), (255, 255, 255, 255))
    cd = ImageDraw.Draw(card)
    cd.rectangle([0, 0, card_side - 1, card_side - 1],
                 outline=(255, 255, 255, 255), width=1)

    # QR 読み込み・リサイズ
    if os.path.isfile(QR_PATH):
        try:
            qr = Image.open(QR_PATH).convert("RGB")
            qr = qr.resize((qr_side, qr_side), Image.NEAREST)  # QRは補間しすぎない
            card.paste(qr, (pad, pad))
        except Exception as e:
            print(f"[qr] load error: {e}", file=sys.stderr)
            cd.rectangle([pad, pad, pad + qr_side, pad + qr_side],
                         fill=(220, 220, 220, 255))
    else:
        print(f"[qr] WARNING: QR not found: {QR_PATH}", file=sys.stderr)
        cd.rectangle([pad, pad, pad + qr_side, pad + qr_side],
                     fill=(220, 220, 220, 255))

    base_img.alpha_composite(card, (card_x, card_y))

    # キャプション「友だち追加はこちら」（白カードの上・中央揃え）
    cap = "友だち追加はこちら"
    bbox = draw.textbbox((0, 0), cap, font=f_cap)
    cw = bbox[2] - bbox[0]
    cap_x = card_x + (card_side - cw) // 2 - bbox[0]
    cap_y = card_y - 46
    draw.text((cap_x + 2, cap_y + 2), cap, font=f_cap, fill=(0, 0, 0, 170))
    draw.text((cap_x, cap_y), cap, font=f_cap, fill=LINE_GREEN)


if __name__ == "__main__":
    main()

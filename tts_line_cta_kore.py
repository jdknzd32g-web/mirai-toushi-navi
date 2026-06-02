#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未来投資navi メディア部門 - Gemini TTS ナレーション生成スクリプト
プリセット音声「Kore」で日本語ナレーション(LINE CTA)を /tmp/line_cta_kore.wav に保存する。

確認した公式ドキュメント:
  https://ai.google.dev/gemini-api/docs/speech-generation
使用モデル: gemini-2.5-flash-preview-tts
PCM出力仕様: 24000Hz / 16bit(sampwidth=2) / mono(1ch) / signed little-endian
"""

import os
import re
import sys
import wave

from google import genai
from google.genai import types

# ----------------------------------------------------------------------
# 設定
# ----------------------------------------------------------------------
MODEL = "gemini-2.5-flash-preview-tts"
VOICE = "Kore"
OUTPUT_PATH = "/tmp/line_cta_kore.wav"

NARRATION_TEXT = (
    "今だけ先着で、30分の無料相談と、1ヶ月の体験プラン税込5000円を"
    "ご用意しています。詳しくは概要欄の公式LINEへ。"
)

ENV_FILES = [
    "/Users/satoshioka/.env",
    "/Users/satoshioka/mirai-toushi-navi/.env",
    "/Users/satoshioka/youtube-project-share/.env",
]
ENV_KEY = "GOOGLE_GENERATIVE_AI_API_KEY"

# PCMデフォルト(mimeTypeにrateが無い場合のフォールバック)
DEFAULT_RATE = 24000
SAMPLE_WIDTH = 2  # 16bit
CHANNELS = 1      # mono


# ----------------------------------------------------------------------
# APIキー読み込み
# ----------------------------------------------------------------------
def load_api_key():
    # 1) 環境変数に既にあれば優先
    env_val = os.environ.get(ENV_KEY)
    if env_val and env_val.strip():
        return env_val.strip().strip('"').strip("'")

    # 2) .env ファイルを順に探す
    for path in ENV_FILES:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(ENV_KEY + "="):
                        value = line[len(ENV_KEY) + 1:].strip()
                        # 前後のクォート除去
                        value = value.strip('"').strip("'")
                        if value:
                            print(f"[INFO] APIキーを読み込みました: {path}")
                            return value
        except Exception as e:
            print(f"[WARN] {path} の読み込みに失敗: {e}", file=sys.stderr)

    raise RuntimeError(
        f"{ENV_KEY} が見つかりません。"
        f"環境変数または次のいずれかに設定してください: {', '.join(ENV_FILES)}"
    )


# ----------------------------------------------------------------------
# mimeType から sample rate を取り出す (例: "audio/L16;rate=24000")
# ----------------------------------------------------------------------
def parse_rate_from_mime(mime_type):
    if not mime_type:
        return DEFAULT_RATE
    m = re.search(r"rate=(\d+)", mime_type)
    if m:
        return int(m.group(1))
    return DEFAULT_RATE


# ----------------------------------------------------------------------
# wavファイル書き出し
# ----------------------------------------------------------------------
def write_wav(filename, pcm_bytes, rate, sample_width=SAMPLE_WIDTH, channels=CHANNELS):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_bytes)


# ----------------------------------------------------------------------
# メイン
# ----------------------------------------------------------------------
def main():
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    print(f"[INFO] モデル: {MODEL} / 音声: {VOICE}")
    print(f"[INFO] テキスト: {NARRATION_TEXT}")

    response = client.models.generate_content(
        model=MODEL,
        contents=NARRATION_TEXT,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=VOICE,
                    )
                )
            ),
        ),
    )

    # 音声パートを取り出す
    try:
        part = response.candidates[0].content.parts[0]
        inline = part.inline_data
        pcm_bytes = inline.data
        mime_type = getattr(inline, "mime_type", None)
    except (AttributeError, IndexError, TypeError) as e:
        raise RuntimeError(
            f"音声データの取得に失敗しました。レスポンス構造を確認してください: {e}\n"
            f"response={response}"
        )

    if not pcm_bytes:
        raise RuntimeError("音声データが空でした。テキストやモデル名を確認してください。")

    rate = parse_rate_from_mime(mime_type)
    print(f"[INFO] inline mimeType: {mime_type} -> sample rate {rate}Hz")

    write_wav(OUTPUT_PATH, pcm_bytes, rate=rate)

    # 結果表示
    size_bytes = os.path.getsize(OUTPUT_PATH)
    num_frames = len(pcm_bytes) // (SAMPLE_WIDTH * CHANNELS)
    duration_sec = num_frames / float(rate)

    print("-" * 50)
    print(f"[OK] 保存パス : {OUTPUT_PATH}")
    print(f"[OK] ファイルサイズ : {size_bytes:,} bytes ({size_bytes / 1024:.1f} KB)")
    print(f"[OK] 音声の長さ : {duration_sec:.2f} 秒")
    print("-" * 50)


if __name__ == "__main__":
    main()

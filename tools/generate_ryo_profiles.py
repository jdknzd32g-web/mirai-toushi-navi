# -*- coding: utf-8 -*-
import os
import sys
import time
from pathlib import Path
from PIL import Image
import io

ROOT = Path("/Users/satoshioka/mirai-toushi-navi")
sys.path.append(str(ROOT))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
load_dotenv("/Users/satoshioka/youtube-project-share/.env")

# Reference image path
REF_IMAGE = Path("/Users/satoshioka/youtube-project-share/transcription-system/_apps/thumbnail/output/ryo_expressions/expr_04_serious.jpg")

# Output paths
TOP_IMAGE_OUT = ROOT / "images/ryo-profile.png"
BOTTOM_IMAGE_OUT = ROOT / "images/ryo-profile2.png"

# Identity base description
IDENTITY_BASE = (
    "Using the reference photo as the identity source: "
    "Generate a photorealistic bust-up portrait of this exact same person "
    "(Japanese man, blonde hair, black rectangular Wellington eyeglasses, "
    "grey jacket over white T-shirt). "
    "The background must be a completely solid, flat, uniform dark blue color of exactly hex #0a0f24. "
    "Absolutely no textures, no gradients, no shadows, no vignette, and no lighting variations in the background. "
    "It must be a 100% flat uniform #0a0f24 color to seamlessly blend with the web page. "
    "Keep the same face identity, hair color, glasses style, and jacket. "
)

def generate_image(client, prompt_suffix, ref_path):
    from google.genai import types
    prompt_text = IDENTITY_BASE + prompt_suffix
    ref_bytes = ref_path.read_bytes()
    mime_type = "image/jpeg"

    print(f"Calling gemini-3.1-flash-image-preview with prompt:\n  {prompt_text}\n")
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[
                types.Part.from_bytes(data=ref_bytes, mime_type=mime_type),
                types.Part.from_text(text=prompt_text),
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

def main():
    api_key = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: API key not found. Please set GOOGLE_GENERATIVE_AI_API_KEY in .env")
        sys.exit(1)

    if not REF_IMAGE.exists():
        print(f"ERROR: Reference image not found at {REF_IMAGE}")
        sys.exit(1)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except ImportError:
        print("ERROR: google-genai SDK not found. Install it with pip install google-genai")
        sys.exit(1)

    # 1. Top Image (Friendly smile, looking directly at the camera)
    print("=== Generating TOP image (ryo-profile.png) ===")
    top_prompt_suffix = "Expression: a warm, friendly and confident smile, looking directly at the camera with a welcoming look."
    top_bytes = generate_image(client, top_prompt_suffix, REF_IMAGE)
    if top_bytes:
        img = Image.open(io.BytesIO(top_bytes))
        img.save(TOP_IMAGE_OUT, "PNG")
        print(f"SUCCESS: Saved top image to {TOP_IMAGE_OUT} ({len(top_bytes)//1024} KB)\n")
    else:
        print("FAILED to generate top image.\n")

    # Rate limiting sleep
    time.sleep(3)

    # 2. Bottom Image (Friendly smile, diagonal three-quarter angle view)
    print("=== Generating BOTTOM image (ryo-profile2.png) ===")
    bottom_prompt_suffix = "Angle: taken from a diagonal angle (three-quarter view). Expression: a bright, friendly and engaging smile, looking slightly off-camera with a welcoming face."
    bottom_bytes = generate_image(client, bottom_prompt_suffix, REF_IMAGE)
    if bottom_bytes:
        img = Image.open(io.BytesIO(bottom_bytes))
        img.save(BOTTOM_IMAGE_OUT, "PNG")
        print(f"SUCCESS: Saved bottom image to {BOTTOM_IMAGE_OUT} ({len(bottom_bytes)//1024} KB)\n")
    else:
        print("FAILED to generate bottom image.\n")

if __name__ == "__main__":
    main()

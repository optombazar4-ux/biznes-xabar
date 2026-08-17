"""Ixtiyoriy: rasm topilmagan maqolalar uchun Gemini bilan rasm generatsiya.

.env orqali yoqiladi: IMAGE_GENERATION=true (standart: o'chiq — har rasm pullik).
Production'da WebP rasm Supabase Storage'ga, lokalda MEDIA_DIR ga saqlanadi.
"""

import base64
from io import BytesIO
from pathlib import Path
import re

import httpx
from PIL import Image

from ..config import (
    BACKEND_PUBLIC_URL,
    GEMINI_API_KEY,
    GEMINI_IMAGE_MODEL,
    MEDIA_DIR,
)
from .storage import upload_bytes


def _compress_webp(image_bytes: bytes) -> bytes:
    """Rasmni bepul Storage va tez sahifa uchun o'lchamlangan WebP qiladi."""
    with Image.open(BytesIO(image_bytes)) as image:
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGB")
        output = BytesIO()
        image.save(output, format="WEBP", quality=82, method=6)
        return output.getvalue()


def generate_image(title: str, slug: str) -> str | None:
    """Sarlavha asosida yangilik illyustratsiyasini yaratadi.
    Muvaffaqiyatda ommaviy URL, xatoda None qaytaradi."""
    if not GEMINI_API_KEY:
        return None

    prompt = (
        "Create a clean, modern editorial illustration for a technology news "
        f"article titled: \"{title}\". Abstract tech aesthetic, blue and dark "
        "tones, suitable as a news cover image. No text, no letters, no logos."
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_IMAGE_MODEL}:generateContent"
    )
    try:
        response = httpx.post(
            url,
            json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]},
            headers={"x-goog-api-key": GEMINI_API_KEY},
            timeout=120,
        )
        if response.status_code != 200:
            print(f"   ✗ Rasm generatsiya xatosi {response.status_code}: {response.text[:200]}")
            return None

        parts = response.json()["candidates"][0]["content"]["parts"]
        image_part = next((p["inlineData"] for p in parts if "inlineData" in p), None)
        if not image_part:
            return None

        raw_image = base64.b64decode(image_part["data"])
        webp_image = _compress_webp(raw_image)
        safe_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", slug or "cover")
        filename = f"{safe_slug}.webp"

        storage_url = upload_bytes(
            f"images/{filename}",
            webp_image,
            "image/webp",
        )
        if storage_url:
            return storage_url

        media_dir = Path(MEDIA_DIR)
        media_dir.mkdir(parents=True, exist_ok=True)
        file_path = media_dir / filename
        file_path.write_bytes(webp_image)
        return f"{BACKEND_PUBLIC_URL}/media/{filename}"
    except Exception as error:
        print(f"   ✗ Rasm generatsiya xatosi: {error}")
        return None

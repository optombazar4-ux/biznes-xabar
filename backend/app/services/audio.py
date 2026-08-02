"""O'zbekcha Text-to-Speech (TTS) Audio Generatsiya Servisi.

Maqola sarlavhasi, xulosasi va amaliy ahamiyatidan MP3 audio fayl tayyorlaydi
hamda /media/audio/ papkasida keshlab saqlaydi.
"""

import os
import urllib.parse
from pathlib import Path
import httpx

from ..config import MEDIA_DIR, BACKEND_PUBLIC_URL

AUDIO_DIR = Path(MEDIA_DIR) / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def generate_article_audio(slug: str, title: str, summary: str, practical_note: str | None = None) -> str:
    """Maqola matnidan MP3 audio fayl yaratadi yoki mavjud keshlangan fayl URL'ini qaytaradi."""
    filename = f"{slug}.mp3"
    filepath = AUDIO_DIR / filename
    public_url = f"{BACKEND_PUBLIC_URL}/media/audio/{filename}"

    # 1. Agar audio allaqachon yaratilgan va 0 bayt bo'lmasa, tayyor URL qaytaramiz
    if filepath.exists() and filepath.stat().st_size > 1000:
        return public_url

    # 2. Ovozga aylantiriladigan matn
    text_to_speak = f"{title}. {summary}"
    if practical_note:
        text_to_speak += f" Bu nima degani? {practical_note}"

    # Textni qisqartirish (TTS so'rov chegarasiga moslash)
    clean_text = " ".join(text_to_speak.split())[:1000]

    # 3. Google Translate TTS API yordamida audio olamiz (uzbek tili 'uz')
    try:
        encoded_text = urllib.parse.quote(clean_text)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=uz&client=tw-ob"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(tts_url, headers=headers)
            if resp.status_code == 200 and len(resp.content) > 500:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                return public_url
    except Exception as err:
        print(f"⚠️ TTS audio generatsiyasida xatolik ({err})")

    return ""

"""O'zbekcha Text-to-Speech (TTS) Audio Generatsiya Servisi.

Gemini 3.1 Flash TTS model (`gemini-3.1-flash-tts-preview`) hamda fallback TTS manbalaridan
foydalanib maqoladan MP3 audio fayl yaratadi va `/media/audio/` papkasida keshlaydi.
"""

import os
import urllib.parse
from pathlib import Path
import httpx

from ..config import MEDIA_DIR, BACKEND_PUBLIC_URL, GEMINI_API_KEY, GEMINI_TTS_MODEL

AUDIO_DIR = Path(MEDIA_DIR) / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def generate_article_audio(slug: str, title: str, summary: str, practical_note: str | None = None) -> str:
    """Maqola matnidan MP3 audio fayl yaratadi yoki keshlangan fayl URL'ini qaytaradi."""
    filename = f"{slug}.mp3"
    filepath = AUDIO_DIR / filename
    public_url = f"{BACKEND_PUBLIC_URL}/media/audio/{filename}"

    # 1. Keshlangan tayyor audio bo'lsa
    if filepath.exists() and filepath.stat().st_size > 1000:
        return public_url

    # 2. Ovozlantiriladigan toza matn
    text_to_speak = f"{title}. {summary}"
    if practical_note:
        text_to_speak += f" Bu nima degani? {practical_note}"
    clean_text = " ".join(text_to_speak.split())[:1200]

    # 3. Usul 1: Gemini 3.1 Flash TTS Preview (agar GEMINI_API_KEY bo'lsa)
    if GEMINI_API_KEY:
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_TTS_MODEL}:generateContent?key={GEMINI_API_KEY}"
            prompt = f"Quyidagi dars matnini o'zbek tilida aniq, ravon va yoqimli ovozda o'qib ber:\n\n{clean_text}"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "audio/mp3"
                }
            }
            with httpx.Client(timeout=25.0) as client:
                resp = client.post(gemini_url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    # Audio data base64 yoki inline_data orqali kelishini tekshiramiz
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    for part in parts:
                        inline = part.get("inlineData") or part.get("inline_data")
                        if inline and inline.get("data"):
                            import base64
                            audio_bytes = base64.b64decode(inline["data"])
                            if len(audio_bytes) > 500:
                                with open(filepath, "wb") as f:
                                    f.write(audio_bytes)
                                print(f"✅ Gemini TTS ({GEMINI_TTS_MODEL}) audio yaratildi: {filename}")
                                return public_url
        except Exception as err:
            print(f"⚠️ Gemini TTS xatosi ({err}), fallback Google TTS ga o'tilmoqda...")

    # 4. Usul 2: Google TTS Fallback (O'zbek tili 'uz')
    try:
        encoded_text = urllib.parse.quote(clean_text[:800])
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=uz&client=tw-ob"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(tts_url, headers=headers)
            if resp.status_code == 200 and len(resp.content) > 500:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                print(f"✅ Google TTS audio yaratildi: {filename}")
                return public_url
    except Exception as err:
        print(f"❌ Fallback TTS xatosi: {err}")

    return ""

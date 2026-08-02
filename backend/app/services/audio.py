"""O'zbekcha Text-to-Speech (TTS) Audio Generatsiya Servisi.

EdgeTTS (uz-UZ-MadinaNeural) va Gemini 3.1 Flash TTS model (`gemini-3.1-flash-tts-preview`)
yordamida maqola matnidan ravon o'zbekcha MP3 audio yaratadi hamda /media/audio/ papkasida keshlaydi.
"""

import asyncio
import os
import sys
import urllib.parse
from pathlib import Path
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")


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
    clean_text = " ".join(text_to_speak.split())[:2000]

    # 3. Primary: EdgeTTS O'zbek Tili (uz-UZ-MadinaNeural — juda sifatli va tabiiy ovoz)
    try:
        import edge_tts
        communicate = edge_tts.Communicate(clean_text, "uz-UZ-MadinaNeural")
        asyncio.run(communicate.save(str(filepath)))
        if filepath.exists() and filepath.stat().st_size > 1000:
            print(f"✅ EdgeTTS (uz-UZ-MadinaNeural) o'zbekcha audio yaratildi: {filename}")
            return public_url
    except Exception as err:
        print(f"⚠️ EdgeTTS xatosi ({err}), Gemini TTS ga o'tilmoqda...")

    # 4. Secondary: Gemini 3.1 Flash TTS Preview (agar GEMINI_API_KEY bo'lsa)
    if GEMINI_API_KEY:
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_TTS_MODEL}:generateContent?key={GEMINI_API_KEY}"
            prompt = f"Quyidagi dars matnini o'zbek tilida aniq, ravon va yoqimli ovozda o'qib ber:\n\n{clean_text}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "audio/mp3"}
            }
            with httpx.Client(timeout=25.0) as client:
                resp = client.post(gemini_url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
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
            print(f"⚠️ Gemini TTS xatosi ({err})")

    return ""

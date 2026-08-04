"""O'zbekcha Text-to-Speech (TTS) Audio Generatsiya Servisi.

EdgeTTS (uz-UZ-MadinaNeural), Google Gemini TTS (`gemini-3.1-flash-tts-preview`) hamda
gTTS yordamida har bir dars uchun o'zbekcha audio fayl yaratadi hamda keshlaydi.
"""

import asyncio
import base64
import concurrent.futures
import os
import re
import sys
import wave
from pathlib import Path
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

from ..config import MEDIA_DIR, BACKEND_PUBLIC_URL, GEMINI_API_KEY, GEMINI_TTS_MODEL

AUDIO_DIR = Path(MEDIA_DIR) / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Minimal fallback audio
SILENT_MP3_FRAME = b"\xff\xf3\x18\xc4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" * 80


async def _async_edge_tts_save(text: str, dest_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, "uz-UZ-MadinaNeural")
    await communicate.save(dest_path)


def _generate_gemini_audio(text: str, wav_path: Path) -> bool:
    """Rasmiy Google GenAI SDK orqali Gemini TTS audio (AUDIO modaliteti) yaratadi."""
    if not GEMINI_API_KEY:
        return False
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"Quyidagi dars matnini o'zbek tilida aniq va ravon o'qib ber:\n\n{text}"
        
        model_name = GEMINI_TTS_MODEL if "flash" in GEMINI_TTS_MODEL else "gemini-2.5-flash"
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"
                        )
                    )
                )
            )
        )

        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                audio_bytes = part.inline_data.data
                if isinstance(audio_bytes, str):
                    audio_bytes = base64.b64decode(audio_bytes)
                if len(audio_bytes) > 500:
                    with wave.open(str(wav_path), "wb") as f:
                        f.setnchannels(1)
                        f.setsampwidth(2)
                        f.setframerate(24000)
                        f.writeframes(audio_bytes)
                    print(f"✅ Gemini GenAI SDK Audio yaratildi ({model_name}): {wav_path.name}")
                    return True
    except Exception as err:
        print(f"⚠️ Gemini GenAI SDK TTS xatosi: {err}")
    return False


def generate_article_audio(slug: str, title: str, summary: str, practical_note: str | None = None) -> str:
    """Maqola matnidan MP3/WAV audio fayl yaratadi yoki keshlangan fayl URL'ini qaytaradi."""
    safe_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", slug or "dars")
    
    mp3_filename = f"{safe_slug}.mp3"
    wav_filename = f"{safe_slug}.wav"
    
    mp3_filepath = AUDIO_DIR / mp3_filename
    wav_filepath = AUDIO_DIR / wav_filename

    # 1. Keshlangan fayl mavjud bo'lsa (haqiqatda diskda bor bo'lganini qaytaramiz)
    if mp3_filepath.exists() and mp3_filepath.stat().st_size > 500:
        return f"{BACKEND_PUBLIC_URL}/media/audio/{mp3_filename}"
    if wav_filepath.exists() and wav_filepath.stat().st_size > 500:
        return f"{BACKEND_PUBLIC_URL}/media/audio/{wav_filename}"

    # 2. Ovozlantiriladigan toza matn
    raw_text = f"{title or ''}. {summary or ''}"
    if practical_note:
        raw_text += f" Bu nima degani? {practical_note}"
    clean_text = " ".join(raw_text.split())[:1500]
    if not clean_text:
        clean_text = "Biznes darsi va amaliy tavsiyalar."

    # 3. EdgeTTS O'zbek Tili (uz-UZ-MadinaNeural — barcha brauzerlar va pleerlarda standart ijro etiladigan MP3)
    try:
        def _worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_async_edge_tts_save(clean_text, str(mp3_filepath)))
            finally:
                loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(_worker).result(timeout=15.0)

        if mp3_filepath.exists() and mp3_filepath.stat().st_size > 500:
            print(f"✅ EdgeTTS (uz-UZ-MadinaNeural) audio yaratildi: {mp3_filename}")
            return f"{BACKEND_PUBLIC_URL}/media/audio/{mp3_filename}"
    except Exception as err:
        print(f"⚠️ EdgeTTS xatosi: {err}")

    # 4. Gemini GenAI SDK Audio
    if GEMINI_API_KEY:
        if _generate_gemini_audio(clean_text, wav_filepath):
            return f"{BACKEND_PUBLIC_URL}/media/audio/{wav_filename}"

    # 5. gTTS Fallback (o'zbek tili)
    try:
        from gtts import gTTS
        tts = gTTS(text=clean_text[:500], lang="uz")
        tts.save(str(mp3_filepath))
        if mp3_filepath.exists() and mp3_filepath.stat().st_size > 500:
            return f"{BACKEND_PUBLIC_URL}/media/audio/{mp3_filename}"
    except Exception as err:
        print(f"⚠️ gTTS xatosi: {err}")

    # 6. Fallback silent MP3
    try:
        with open(mp3_filepath, "wb") as f:
            f.write(SILENT_MP3_FRAME)
        return f"{BACKEND_PUBLIC_URL}/media/audio/{mp3_filename}"
    except Exception as err:
        print(f"❌ Fallback audio xatosi: {err}")
        return f"{BACKEND_PUBLIC_URL}/media/audio/{mp3_filename}"

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv()

# Ma'lumotlar bazasi: prod'da PostgreSQL, lokal ishlab chiqishda SQLite yetarli.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biznesxabar.db")

# AI provayder: "gemini" (standart) yoki "claude"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Render kabi Google Cloud'dan tashqaridagi serverlar uchun Vertex AI + ADC.
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
VERTEX_GEMINI_MODEL = os.getenv("VERTEX_GEMINI_MODEL", "gemini-2.5-flash-lite")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-8")

# Admin panelga kirish uchun maxfiy token (X-Admin-Token sarlavhasi yoki JWT orqali).
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()
UNSAFE_ADMIN_TOKENS = {
    "biznesdarslari2026adminsecret202608",
    "admin-token-o'zgartiring",
    "maxfiy-admin-token",
    "bu-yerga-kuchli-tasodifiy-token-kiriting",
}

# JWT sozlamalari
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip() or ADMIN_TOKEN
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 soat




def admin_is_configured() -> bool:
    return (
        len(ADMIN_TOKEN) >= 24
        and ADMIN_TOKEN not in UNSAFE_ADMIN_TOKENS
        and len(JWT_SECRET_KEY) >= 24
    )



def validate_production_settings() -> None:
    """Xavfli admin token haqida ogohlantiradi; public API'ni yiqitmaydi."""
    if not admin_is_configured():
        print(
            "OGOHLANTIRISH: ADMIN_TOKEN xavfsiz sozlanmagan. "
            "Admin endpointlari yangi kuchli token berilguncha bloklandi."
        )

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")  # masalan: @biznesxabari


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "ha")


# Render'dagi yagona web service pipeline va botni API jarayonida ishlatadi.
# Docker Compose'da ular alohida servis bo'lgani uchun false beriladi.
RUN_BACKGROUND_SERVICES = _bool("RUN_BACKGROUND_SERVICES", "true")

# Kuratsiya qilingan katalog tugagach, xalqaro biznes RSS trendlaridan
# O'zbekistonga mos yangi g'oyalar har kuni taklif qilinadi.
RSS_IDEA_ENABLED = _bool("RSS_IDEA_ENABLED", "true")
RSS_IDEA_INTERVAL_DAYS = max(1, int(os.getenv("RSS_IDEA_INTERVAL_DAYS", "1")))
RSS_IDEA_SUGGESTIONS_PER_BATCH = max(
    5, min(10, int(os.getenv("RSS_IDEA_SUGGESTIONS_PER_BATCH", "8")))
)
RSS_FEED_ITEMS_PER_SOURCE = max(
    3, min(10, int(os.getenv("RSS_FEED_ITEMS_PER_SOURCE", "5")))
)


# Avto-chop etish: pipeline maqolalarni admin tasdig'isiz to'g'ridan-to'g'ri
# saytga chiqaradi. O'chirish uchun: AUTO_PUBLISH=false
AUTO_PUBLISH = _bool("AUTO_PUBLISH", "true")
# Faqat shu bahodan yuqori maqolalar avto-chop etiladi (qolganlari pending)
AUTO_PUBLISH_MIN_IMPORTANCE = int(os.getenv("AUTO_PUBLISH_MIN_IMPORTANCE", "1"))

# Muhim yangiliklarni Telegram kanalga avtomatik yuborish
AUTO_TELEGRAM = _bool("AUTO_TELEGRAM", "true")
AUTO_TELEGRAM_MIN_IMPORTANCE = int(os.getenv("AUTO_TELEGRAM_MIN_IMPORTANCE", "4"))

# Rasm topilmaganda Gemini bilan generatsiya qilish (pullik — standart o'chiq)
IMAGE_GENERATION = _bool("IMAGE_GENERATION", "false")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
GEMINI_TTS_MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-3.1-flash-tts-preview")

# Yaratilgan rasmlar saqlanadigan papka va ularning ommaviy manzili
MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")

# Frontend manzili (CORS uchun)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", FRONTEND_ORIGIN)

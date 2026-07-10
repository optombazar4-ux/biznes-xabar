"""Telegram kanaliga post yuborish (Bot API orqali)."""

import html

import httpx

from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, FRONTEND_ORIGIN
from ..models import Article


def format_post(article: Article) -> str:
    category = article.category.name if article.category else "Biznes darsi"
    return (
        f"🎓 <b>{html.escape(article.title)}</b>\n\n"
        f"{html.escape(article.summary)}\n\n"
        f"💡 <i>{html.escape(article.practical_note)}</i>\n\n"
        f"📂 {html.escape(category)}"
    )


def build_reply_markup(article: Article) -> dict:
    """Darsni saytda to'liq o'qish uchun tugma (toza URL: /{bo'lim}/{slug})."""
    cat_slug = article.category.slug if article.category else "biznesni-boshlash"
    return {
        "inline_keyboard": [
            [{"text": "📖 Darsni to'liq o'qish", "url": f"{FRONTEND_ORIGIN}/{cat_slug}/{article.slug}"}],
        ]
    }


def send_to_channel(article: Article) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN yoki TELEGRAM_CHANNEL_ID sozlanmagan")

    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    text = format_post(article)
    reply_markup = build_reply_markup(article)

    if article.image_url:
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "photo": article.image_url,
            "caption": text[:1024],
            "parse_mode": "HTML",
            "reply_markup": reply_markup,
        }
        response = httpx.post(f"{api}/sendPhoto", json=payload, timeout=30)
    else:
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text[:4096],
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "reply_markup": reply_markup,
        }
        response = httpx.post(f"{api}/sendMessage", json=payload, timeout=30)

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram xatosi: {data.get('description')}")

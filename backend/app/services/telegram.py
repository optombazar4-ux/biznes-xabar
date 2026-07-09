"""Telegram kanaliga post yuborish (Bot API orqali)."""

import html

import httpx

from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, FRONTEND_ORIGIN
from ..models import Article


def format_post(article: Article) -> str:
    stars = "⭐" * max(1, min(5, article.importance))
    category = article.category.name if article.category else "AI"
    return (
        f"<b>{html.escape(article.title)}</b>\n\n"
        f"{html.escape(article.summary)}\n\n"
        f"💡 <i>{html.escape(article.practical_note)}</i>\n\n"
        f"📂 {html.escape(category)} | Ahamiyati: {stars}"
    )


def build_reply_markup(article: Article) -> dict:
    """Asl manba va Batafsil o'qish tugmalarini alohida bosiladigan tugma qatorlariga chiqaradi."""
    return {
        "inline_keyboard": [
            [{"text": "🔗 Asl manba", "url": article.original_url}],
            [{"text": "📖 Batafsil o'qish", "url": f"{FRONTEND_ORIGIN}/maqola/{article.slug}"}],
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

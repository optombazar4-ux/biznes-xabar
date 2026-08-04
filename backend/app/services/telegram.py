"""Telegram kanaliga post yuborish (Bot API orqali)."""

import html

import httpx

from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, FRONTEND_ORIGIN
from ..models import Article


def _truncate(value: str | None, limit: int) -> str:
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1].rstrip()}…"


def format_post(article: Article, *, compact: bool = False) -> str:
    title_limit = 160 if compact else 300
    summary_limit = 460 if compact else 1400
    practical_limit = 180 if compact else 600
    category = _truncate(
        article.category.name if article.category else "Biznes darsi",
        80,
    )
    
    tags_text = ""
    if article.tags and isinstance(article.tags, list):
        hashtags = [f"#{tag.replace(' ', '_').replace('-', '_')}" for tag in article.tags if tag]
        if hashtags:
            tags_text = "\n\n" + " ".join(hashtags[:5])

    return (
        f"🎓 <b>{html.escape(_truncate(article.title, title_limit))}</b>\n\n"
        f"{html.escape(_truncate(article.summary, summary_limit))}\n\n"
        f"💡 <i>{html.escape(_truncate(article.practical_note, practical_limit))}</i>\n\n"
        f"📂 {html.escape(category)}{tags_text}"
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
    reply_markup = build_reply_markup(article)

    if article.image_url:
        text = format_post(article, compact=True)
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "photo": article.image_url,
            "caption": text,
            "parse_mode": "HTML",
            "reply_markup": reply_markup,
        }
        try:
            response = httpx.post(f"{api}/sendPhoto", json=payload, timeout=30)
        except httpx.RequestError:
            raise RuntimeError("Telegram tarmoq xatosi") from None
    else:
        text = format_post(article)
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "reply_markup": reply_markup,
        }
        try:
            response = httpx.post(f"{api}/sendMessage", json=payload, timeout=30)
        except httpx.RequestError:
            raise RuntimeError("Telegram tarmoq xatosi") from None

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram xatosi: {data.get('description')}")

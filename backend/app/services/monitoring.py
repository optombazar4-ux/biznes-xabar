"""Pipeline xatolari uchun maxfiy ma'lumotsiz tashqi ogohlantirishlar."""

import logging
import re
from datetime import datetime, timezone

import httpx

from ..config import PIPELINE_ALERT_WEBHOOK_URL

logger = logging.getLogger("biznesdarslari.monitoring")

_TELEGRAM_TOKEN_RE = re.compile(r"(api\.telegram\.org/bot)[^/\s]+", re.IGNORECASE)
_URL_CREDENTIAL_RE = re.compile(
    r"([a-z][a-z0-9+.-]*://[^:/\s]+:)[^@/\s]+@",
    re.IGNORECASE,
)


def sanitize_error(error: BaseException | str, limit: int = 1000) -> str:
    """Log yoki auditga yozishdan oldin URL ichidagi sirlarni yashiradi."""
    message = str(error)
    message = _TELEGRAM_TOKEN_RE.sub(r"\1[REDACTED]", message)
    message = _URL_CREDENTIAL_RE.sub(r"\1[REDACTED]@", message)
    return message[:limit]


async def send_pipeline_alert(error: BaseException | str) -> bool:
    """Sozlangan webhook'ka oddiy JSON alert yuboradi.

    URL bo'sh bo'lsa hech narsa qilmaydi. Webhook siri URL ichida bo'lishi
    mumkinligi sababli URL yoki response body loglanmaydi.
    """
    if not PIPELINE_ALERT_WEBHOOK_URL:
        return False

    payload = {
        "service": "biznes-xabar-backend",
        "event": "pipeline_failed",
        "status": "error",
        "message": sanitize_error(error),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(PIPELINE_ALERT_WEBHOOK_URL, json=payload)
            response.raise_for_status()
        return True
    except Exception as alert_error:
        logger.warning(
            "Pipeline alert yuborilmadi (%s).",
            type(alert_error).__name__,
        )
        return False

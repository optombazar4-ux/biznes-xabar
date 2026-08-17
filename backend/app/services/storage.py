"""Supabase Storage uchun kichik, server-only REST adapter.

Service-role kaliti faqat Render backend environment'ida turadi. Public bucket
fayllari CDN URL orqali beriladi; konfiguratsiya bo'lmasa chaqiruvchilar lokal
MEDIA_DIR fallback'iga qaytadi.
"""

import logging
from pathlib import Path
from urllib.parse import quote

import httpx

from ..config import (
    STORAGE_MAX_FILE_MB,
    SUPABASE_SECRET_KEY,
    SUPABASE_STORAGE_BUCKET,
    SUPABASE_URL,
)

logger = logging.getLogger("biznesdarslari.storage")


def storage_is_configured() -> bool:
    return bool(
        SUPABASE_URL
        and SUPABASE_SECRET_KEY
        and SUPABASE_STORAGE_BUCKET
    )


def _clean_object_path(object_path: str) -> str:
    parts = [part for part in object_path.replace("\\", "/").split("/") if part]
    if not parts or any(part in {".", ".."} for part in parts):
        raise ValueError("Noto'g'ri Storage object path")
    return "/".join(parts)


def public_object_url(object_path: str) -> str | None:
    if not storage_is_configured():
        return None
    clean_path = _clean_object_path(object_path)
    encoded_bucket = quote(SUPABASE_STORAGE_BUCKET, safe="")
    encoded_path = quote(clean_path, safe="/")
    return (
        f"{SUPABASE_URL}/storage/v1/object/public/"
        f"{encoded_bucket}/{encoded_path}"
    )


def existing_public_object_url(object_path: str) -> str | None:
    """Public object mavjud bo'lsa URL qaytaradi; tarmoq xatosida cache miss."""
    url = public_object_url(object_path)
    if not url:
        return None
    try:
        response = httpx.head(url, timeout=8.0, follow_redirects=True)
        return url if response.status_code == 200 else None
    except httpx.HTTPError:
        return None


def upload_bytes(
    object_path: str,
    content: bytes,
    content_type: str,
    *,
    cache_control: str = "31536000",
) -> str | None:
    """Kichik faylni public bucket'ga upsert qiladi va CDN URL qaytaradi."""
    if not storage_is_configured():
        return None
    if not content:
        return None

    max_bytes = STORAGE_MAX_FILE_MB * 1024 * 1024
    if len(content) > max_bytes:
        logger.warning(
            "Storage upload o'tkazildi: fayl limiti %s MB dan katta.",
            STORAGE_MAX_FILE_MB,
        )
        return None

    clean_path = _clean_object_path(object_path)
    encoded_bucket = quote(SUPABASE_STORAGE_BUCKET, safe="")
    encoded_path = quote(clean_path, safe="/")
    upload_url = (
        f"{SUPABASE_URL}/storage/v1/object/{encoded_bucket}/{encoded_path}"
    )
    headers = {
        "apikey": SUPABASE_SECRET_KEY,
        "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
        "Content-Type": content_type,
        "Content-Length": str(len(content)),
        "cache-control": cache_control,
        "x-upsert": "true",
    }
    try:
        response = httpx.post(
            upload_url,
            content=content,
            headers=headers,
            timeout=60.0,
        )
        response.raise_for_status()
        return public_object_url(clean_path)
    except httpx.HTTPError as error:
        logger.warning(
            "Supabase Storage upload bajarilmadi (%s).",
            type(error).__name__,
        )
        return None


def upload_file(
    object_path: str,
    file_path: Path,
    content_type: str,
    *,
    cache_control: str = "31536000",
) -> str | None:
    try:
        content = file_path.read_bytes()
    except OSError:
        return None
    return upload_bytes(
        object_path,
        content,
        content_type,
        cache_control=cache_control,
    )

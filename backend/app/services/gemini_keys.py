"""Gemini API kalitlari rotatsiyasi: kvota (429) tugasa navbatdagi kalitga o'tadi."""

import httpx

from ..config import GEMINI_EXTRA_API_KEYS


def gemini_keys(primary_key: str) -> list[str]:
    """GEMINI_API_KEY va GEMINI_API_KEY1..3 — takrorlarsiz, tartib saqlangan."""
    return list(
        dict.fromkeys(key for key in (primary_key, *GEMINI_EXTRA_API_KEYS) if key)
    )


def post_gemini(
    url: str, payload: dict, primary_key: str, timeout: int = 60
) -> httpx.Response:
    """429 qaytsa keyingi API kalit bilan qayta urinadi; oxirgi javobni qaytaradi."""
    keys = gemini_keys(primary_key)
    response = None
    for index, key in enumerate(keys):
        response = httpx.post(
            url,
            json=payload,
            headers={"x-goog-api-key": key},
            timeout=timeout,
        )
        if response.status_code != 429:
            return response
        if index + 1 < len(keys):
            print(f"   ⚠ Gemini kvota (429): API kalit #{index + 2} ga o'tilmoqda")
    return response

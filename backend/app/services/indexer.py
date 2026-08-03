"""IndexNow va Instant Search Engine Indexing Pinger.

Yangi dars yoki maqola chop etilganda Yandex, Bing va Google botlariga
lahzalik API bildirishnomasi (Instant Indexing) yuboradi.
"""

import logging
import httpx

INDEXNOW_KEY = "b8f9e61284d74a129031c2b5368a734a"
HOST = "biznesdarslari.uz"
KEY_LOCATION = f"https://{HOST}/b8f9e61284d74a129031c2b5368a734a.txt"

INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://yandex.com/indexnow",
    "https://www.bing.com/indexnow",
]

logger = logging.getLogger(__name__)


def ping_search_engines(urls: list[str]) -> bool:
    """Yangi URL'larni IndexNow (Yandex/Bing) orqali zudlik bilan indekslashga yuboradi."""
    if not urls:
        return False

    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }

    success = False
    with httpx.Client(timeout=5.0) as client:
        for endpoint in INDEXNOW_ENDPOINTS:
            try:
                res = client.post(endpoint, json=payload)
                if res.status_code in (200, 202):
                    logger.info(f"✓ IndexNow success via {endpoint}: {len(urls)} URLs")
                    success = True
            except Exception as err:
                logger.warning(f"✗ IndexNow ping error ({endpoint}): {err}")

    return success

"""IP asosidagi rate limit: production'da umumiy DB, testlarda local fallback."""

from collections import defaultdict, deque
from datetime import timedelta
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import TRUST_PROXY_HEADERS
from .models import RateLimitBucket
from .utils import utcnow_naive

_requests: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def _client_ip(request: Request) -> str:
    """Ishonchli proxy bo'lsa, haqiqiy mijozning birinchi IP manzilini oladi."""
    if TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()[:64] or "unknown"
    return (request.client.host if request.client else "unknown")[:64]


def _too_many_requests(retry_after: int) -> HTTPException:
    return HTTPException(
        status_code=429,
        detail="Juda ko‘p so‘rov yuborildi. Keyinroq qayta urinib ko‘ring.",
        headers={"Retry-After": str(max(1, retry_after))},
    )


def _enforce_in_memory(key: str, limit: int, window_seconds: int) -> None:
    """Bazaga ulanmagan unit-test va lokal fallback uchun."""
    now = monotonic()
    cutoff = now - window_seconds
    with _lock:
        bucket = _requests[key]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            raise _too_many_requests(int(window_seconds - (now - bucket[0])))
        bucket.append(now)


def _enforce_in_database(
    db: Session, key: str, limit: int, window_seconds: int
) -> None:
    """PostgreSQL advisory lock bilan instance'lar orasida atomar cheklov."""
    now = utcnow_naive()
    expires_at = now + timedelta(seconds=window_seconds)

    if db.get_bind().dialect.name == "postgresql":
        db.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": key}
        )

    # Shaxsiy IP ma'lumotlari faqat faol oynada saqlanishi uchun eskilarni o'chiramiz.
    db.query(RateLimitBucket).filter(RateLimitBucket.expires_at <= now).delete(
        synchronize_session=False
    )
    bucket = db.get(RateLimitBucket, key)
    if bucket is None:
        db.add(
            RateLimitBucket(
                key=key,
                requests=1,
                started_at=now,
                expires_at=expires_at,
            )
        )
    elif bucket.expires_at <= now:
        bucket.requests = 1
        bucket.started_at = now
        bucket.expires_at = expires_at
    elif bucket.requests >= limit:
        retry_after = int((bucket.expires_at - now).total_seconds())
        db.rollback()
        raise _too_many_requests(retry_after)
    else:
        bucket.requests += 1

    db.commit()


def enforce_rate_limit(
    request: Request,
    scope: str,
    limit: int,
    window_seconds: int,
    db: Session | None = None,
) -> None:
    """`db` berilganda barcha workerlar uchun yagona rate limitni qo'llaydi."""
    key = f"{scope[:80]}:{_client_ip(request)}"
    if db is None:
        _enforce_in_memory(key, limit, window_seconds)
        return
    _enforce_in_database(db, key, limit, window_seconds)

"""Yengil, bitta instance uchun IP asosidagi rate limit himoyasi."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request

_requests: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def enforce_rate_limit(
    request: Request,
    scope: str,
    limit: int,
    window_seconds: int,
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"{scope}:{client_ip}"
    now = monotonic()
    cutoff = now - window_seconds

    with _lock:
        bucket = _requests[key]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = max(1, int(window_seconds - (now - bucket[0])))
            raise HTTPException(
                status_code=429,
                detail="Juda ko‘p so‘rov yuborildi. Keyinroq qayta urinib ko‘ring.",
                headers={"Retry-After": str(retry_after)},
            )
        bucket.append(now)

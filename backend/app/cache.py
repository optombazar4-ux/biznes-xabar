import time
import json
import logging
from typing import Any, Callable
from functools import wraps
from app.config import REDIS_URL, ENABLE_REDIS_CACHE

logger = logging.getLogger(__name__)

_CACHE_STORE: dict[str, tuple[float, Any]] = {}
_redis_client = None

if ENABLE_REDIS_CACHE and REDIS_URL:
    try:
        import redis
        client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=1)
        client.ping()
        _redis_client = client
        logger.info("Connected to Redis cache successfully.")
    except Exception as err:
        _redis_client = None
        logger.info(f"Redis connection skipped ({err}); using in-memory cache fallback.")


def cache_response(ttl_seconds: int = 600):
    """TTL cache decorator for GET endpoints supporting Redis and In-Memory fallback."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"biznes_xabar:{func.__module__}.{func.__name__}:{args}:{kwargs}"
            
            # Try Redis
            if _redis_client:
                try:
                    cached_val = _redis_client.get(key)
                    if cached_val:
                        return json.loads(cached_val)
                except Exception as err:
                    logger.debug(f"Redis get error ({err}), falling back to memory.")

            # Try In-Memory
            now = time.time()
            if key in _CACHE_STORE:
                exp, data = _CACHE_STORE[key]
                if now < exp:
                    return data

            result = func(*args, **kwargs)

            # Store in Redis
            if _redis_client:
                try:
                    _redis_client.setex(key, ttl_seconds, json.dumps(result, default=str))
                except Exception as err:
                    logger.debug(f"Redis set error ({err}).")

            # Store in Memory
            _CACHE_STORE[key] = (now + ttl_seconds, result)
            return result
        return wrapper
    return decorator


def invalidate_cache():
    """Clear all stored response caches across Redis and Memory."""
    _CACHE_STORE.clear()
    if _redis_client:
        try:
            keys = _redis_client.keys("biznes_xabar:*")
            if keys:
                _redis_client.delete(*keys)
        except Exception as err:
            logger.warning(f"Failed to clear Redis keys: {err}")


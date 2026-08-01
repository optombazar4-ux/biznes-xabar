import time
from typing import Any, Callable

_CACHE_STORE: dict[str, tuple[float, Any]] = {}


def cache_response(ttl_seconds: int = 600):
    """Simple in-memory TTL cache decorator for GET endpoints."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Cache key parsing based on function name and args
            key = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
            now = time.time()
            if key in _CACHE_STORE:
                exp, data = _CACHE_STORE[key]
                if now < exp:
                    return data
            
            result = func(*args, **kwargs)
            _CACHE_STORE[key] = (now + ttl_seconds, result)
            return result
        return wrapper
    return decorator


def invalidate_cache():
    """Clear all stored response caches."""
    _CACHE_STORE.clear()

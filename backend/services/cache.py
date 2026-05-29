import os
import threading
import time

_lock = threading.Lock()
_cache: dict[tuple[str, str, int], tuple[float, list[dict]]] = {}


def _ttl_seconds() -> int:
    return int(os.getenv("SEARCH_CACHE_TTL_SECONDS", "900"))


def _normalize_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def get_cached_search(store: str, query: str, page_size: int) -> list[dict] | None:
    """Return cached search results when present and not expired."""
    key = (store, _normalize_query(query), page_size)
    now = time.time()

    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None

        expires_at, value = entry
        if now >= expires_at:
            del _cache[key]
            return None

        return list(value)


def set_cached_search(
    store: str, query: str, page_size: int, results: list[dict]
) -> None:
    """Store search results with TTL from SEARCH_CACHE_TTL_SECONDS."""
    key = (store, _normalize_query(query), page_size)
    expires_at = time.time() + _ttl_seconds()

    with _lock:
        _cache[key] = (expires_at, list(results))


def clear_cache() -> None:
    """Clear all cached entries (for tests)."""
    with _lock:
        _cache.clear()

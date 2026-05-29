import os
import threading
import time
from collections import defaultdict

from fastapi import HTTPException

_lock = threading.Lock()
_requests: dict[str, list[float]] = defaultdict(list)


def _limit_per_minute() -> int:
    return int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))


def check_rate_limit(client_ip: str) -> None:
    """Raise HTTP 429 when the client exceeds the per-minute request limit."""
    limit = _limit_per_minute()
    now = time.time()
    window_start = now - 60

    with _lock:
        timestamps = _requests[client_ip]
        timestamps[:] = [timestamp for timestamp in timestamps if timestamp > window_start]

        if len(timestamps) >= limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again shortly.",
            )

        timestamps.append(now)


def clear_rate_limits() -> None:
    """Reset rate limit state (for tests)."""
    with _lock:
        _requests.clear()

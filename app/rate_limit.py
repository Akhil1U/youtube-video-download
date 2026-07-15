"""In-memory rate limiting."""

from collections import defaultdict
from threading import Lock
from time import time

from fastapi import HTTPException, Request, WebSocket, status

from app.config import loaded_config


class FixedWindowRateLimiter:
    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str):
        if loaded_config.rate_limit_requests <= 0:
            return

        now = time()
        window_start = now - loaded_config.rate_limit_window_seconds
        with self._lock:
            hits = [
                request_time
                for request_time in self._requests[key]
                if request_time >= window_start
            ]
            if len(hits) >= loaded_config.rate_limit_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                )

            hits.append(now)
            self._requests[key] = hits


rate_limiter = FixedWindowRateLimiter()


def get_client_key(request: Request | WebSocket) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"

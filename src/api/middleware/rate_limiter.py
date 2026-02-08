"""
Rate Limiter Middleware

Simple in-memory IP-based rate limiting.
Aligned with settings:
- ENABLE_RATE_LIMITING
- REQUESTS_PER_MINUTE
"""

import time
import logging
from typing import Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from src.config.settings import get_settings

logger = logging.getLogger("vidhi.rate_limiter")

# ---------------------------------------------------------------------
# In-memory rate limit store
# ---------------------------------------------------------------------
# {
#   "ip": {
#       "count": int,
#       "window_start": float
#   }
# }
# ---------------------------------------------------------------------

_RATE_LIMIT_STORE: Dict[str, Dict[str, float]] = {}

WINDOW_SECONDS = 60  # fixed window (per minute)


async def rate_limiter_middleware(request: Request, call_next):
    settings = get_settings()

    if not settings.ENABLE_RATE_LIMITING:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    max_requests = settings.REQUESTS_PER_MINUTE
    record = _RATE_LIMIT_STORE.get(client_ip)

    # --------------------------------------------------------------
    # New window or first request
    # --------------------------------------------------------------
    if record is None or (now - record["window_start"]) > WINDOW_SECONDS:
        _RATE_LIMIT_STORE[client_ip] = {
            "count": 1,
            "window_start": now,
        }
    else:
        record["count"] += 1

        if record["count"] > max_requests:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                },
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please retry after some time.",
                    "retry_after_seconds": WINDOW_SECONDS,
                },
                headers={
                    "Retry-After": str(WINDOW_SECONDS),
                },
            )

    response = await call_next(request)

    # Optional visibility headers
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(
        max(0, max_requests - _RATE_LIMIT_STORE[client_ip]["count"])
    )
    response.headers["X-RateLimit-Window"] = str(WINDOW_SECONDS)

    return response

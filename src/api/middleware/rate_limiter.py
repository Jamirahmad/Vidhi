"""
Rate Limiter Middleware

Implements a simple in-memory, IP-based rate limiter.
This is suitable for:
- Local development
- Free-tier deployments
- Streamlit / demo usage

For production-scale deployments, replace this with:
- Redis-backed rate limiting
- API Gateway / Load Balancer throttling
"""

import time
import logging
from typing import Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from src.config.settings import get_settings

logger = logging.getLogger("vidhi.rate_limiter")

# ---------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------
# Structure:
# {
#   "ip_address": {
#       "count": int,
#       "window_start": float
#   }
# }
# ---------------------------------------------------------------------

_RATE_LIMIT_STORE: Dict[str, Dict[str, float]] = {}


# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------

async def rate_limiter_middleware(request: Request, call_next):
    settings = get_settings()

    # Rate limiting can be disabled via config (tests / internal usage)
    if not settings.ENABLE_RATE_LIMITING:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    window_size = settings.RATE_LIMIT_WINDOW_SECONDS
    max_requests = settings.RATE_LIMIT_MAX_REQUESTS

    record = _RATE_LIMIT_STORE.get(client_ip)

    # -----------------------------------------------------------------
    # First request from IP or expired window
    # -----------------------------------------------------------------
    if record is None or (current_time - record["window_start"]) > window_size:
        _RATE_LIMIT_STORE[client_ip] = {
            "count": 1,
            "window_start": current_time,
        }
    else:
        record["count"] += 1

        # -------------------------------------------------------------
        # Rate limit exceeded
        # -------------------------------------------------------------
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
                    "message": (
                        "Too many requests. Please slow down and try again later."
                    ),
                    "retry_after_seconds": window_size,
                },
                headers={
                    "Retry-After": str(window_size),
                },
            )

    # -----------------------------------------------------------------
    # Proceed with request
    # -----------------------------------------------------------------
    response = await call_next(request)

    # Optional: expose rate limit headers (useful for UI & debugging)
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Window"] = str(window_size)
    response.headers["X-RateLimit-Remaining"] = str(
        max(0, max_requests - _RATE_LIMIT_STORE[client_ip]["count"])
    )

    return response

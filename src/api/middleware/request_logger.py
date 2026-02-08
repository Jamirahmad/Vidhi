
"""
Request Logging Middleware

Logs incoming HTTP requests and outgoing responses with:
- request_id
- method
- path
- status code
- latency
- client IP

Designed to support:
- Audit logging
- Debugging
- Agent-level tracing correlation
"""

import time
import uuid
import logging

from fastapi import Request
from fastapi.responses import Response

logger = logging.getLogger("vidhi.request_logger")


async def request_logger_middleware(request: Request, call_next):
    """
    Logs request/response lifecycle details.
    """

    request_id = str(uuid.uuid4())
    start_time = time.time()

    client_ip = request.client.host if request.client else "unknown"

    # Attach request_id to request state for downstream usage
    request.state.request_id = request_id

    logger.info(
        "Incoming request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": client_ip,
        },
    )

    try:
        response: Response = await call_next(request)
    except Exception as exc:
        latency_ms = round((time.time() - start_time) * 1000, 2)

        logger.exception(
            "Unhandled exception during request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "latency_ms": latency_ms,
            },
        )
        raise

    latency_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        },
    )

    # Expose request id for UI & debugging
    response.headers["X-Request-ID"] = request_id

    return response

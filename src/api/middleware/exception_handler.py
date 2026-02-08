"""
Centralized API Exception Handling Middleware

Responsibilities:
- Catch and normalize all unhandled exceptions
- Prevent leakage of internal errors or stack traces
- Return consistent, user-safe error responses
- Log errors for audit and debugging
"""

import logging
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("vidhi.api.exceptions")


# ------------------------------------------------------------------
# Standard Error Response Builder
# ------------------------------------------------------------------

def build_error_response(
    *,
    error_code: str,
    message: str,
    details: Dict[str, Any] | None = None,
    http_status: int = 500
) -> JSONResponse:
    return JSONResponse(
        status_code=http_status,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            }
        }
    )


# ------------------------------------------------------------------
# HTTP Exceptions (FastAPI / Starlette)
# ------------------------------------------------------------------

async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    logger.warning(
        "HTTP exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail,
        }
    )

    return build_error_response(
        error_code="HTTP_ERROR",
        message=str(exc.detail),
        http_status=exc.status_code
    )


# ------------------------------------------------------------------
# Validation Errors (Request Models)
# ------------------------------------------------------------------

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    logger.info(
        "Request validation failed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        }
    )

    return build_error_response(
        error_code="VALIDATION_ERROR",
        message="Invalid request payload",
        details={"fields": exc.errors()},
        http_status=422
    )


# ------------------------------------------------------------------
# Unhandled Exceptions (Fail Safe)
# ------------------------------------------------------------------

async def unhandled_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    logger.exception(
        "Unhandled server exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": exc.__class__.__name__,
        }
    )

    return build_error_response(
        error_code="INTERNAL_SERVER_ERROR",
        message=(
            "An unexpected error occurred while processing the request. "
            "Please try again or contact support."
        ),
        http_status=500
    )

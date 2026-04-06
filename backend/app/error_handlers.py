from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.logging_config import log_event


@dataclass
class HttpError(Exception):
    status: int
    code: str
    message: str
    user_message: str


def http_error_payload(err: HttpError) -> Dict[str, Any]:
    return {
        "error": err.message,
        "code": err.code,
        "userMessage": err.user_message,
    }


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HttpError)
    async def _http_error_handler(_: Request, exc: HttpError) -> JSONResponse:
        log_event(
            app.state.request_logger,
            logging.WARNING,
            "http_error",
            code=exc.code,
            status=exc.status,
            error_message=exc.message,
        )
        return JSONResponse(status_code=exc.status, content=http_error_payload(exc))

    @app.exception_handler(Exception)
    async def _generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
        log_event(
            app.state.request_logger,
            logging.ERROR,
            "unhandled_exception",
            error=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc),
                "code": "INTERNAL_ERROR",
                "userMessage": "Something went wrong on the server. Please retry.",
            },
        )

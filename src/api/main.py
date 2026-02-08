"""
Vidhi API Entry Point

This module exposes the FastAPI application instance `app`.
It is used by:
- uvicorn (local runs)
- console script entrypoint (vidhi-api)
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config.settings import get_settings
from src.config.logging_config import configure_logging

from src.api.middleware.request_logger import request_logger_middleware
from src.api.middleware.rate_limiter import rate_limiter_middleware
from src.api.middleware.exception_handler import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

from src.api.routes.health_routes import router as health_router
from src.api.routes.research_routes import router as research_router
from src.api.routes.document_routes import router as document_router
from src.api.routes.compliance_routes import router as compliance_router
from src.api.routes.feedback_routes import router as feedback_router


# ---------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------

def create_app() -> FastAPI:
    settings = get_settings()

    # Configure logging once
    configure_logging()
    logger = logging.getLogger("vidhi.api")

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Vidhi is a multi-agent AI system for legal research, issue identification, "
            "argument structuring, document drafting, and compliance checks. "
            "All outputs are drafts and require human legal review."
        ),
        docs_url="/docs" if settings.ENABLE_API_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
        openapi_url="/openapi.json" if settings.ENABLE_API_DOCS else None,
    )

    # -----------------------------------------------------------------
    # Middleware
    # -----------------------------------------------------------------

    # CORS (Streamlit UI, notebooks, external clients)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request tracing & rate limiting
    app.middleware("http")(request_logger_middleware)
    app.middleware("http")(rate_limiter_middleware)

    # -----------------------------------------------------------------
    # Exception Handlers
    # -----------------------------------------------------------------

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler
    )

    # -----------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------

    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(research_router, prefix="/research", tags=["Research"])
    app.include_router(document_router, prefix="/documents", tags=["Documents"])
    app.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])
    app.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])

    # -----------------------------------------------------------------
    # Lifecycle Hooks
    # -----------------------------------------------------------------

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info(
            "Vidhi API started",
            extra={
                "environment": settings.ENVIRONMENT,
                "version": settings.APP_VERSION,
            },
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Vidhi API shutdown")

    return app


# ---------------------------------------------------------------------
# FastAPI App Instance
# ---------------------------------------------------------------------

app = create_app()


# ---------------------------------------------------------------------
# Local Execution
# ---------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

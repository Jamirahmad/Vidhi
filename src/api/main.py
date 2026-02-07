"""
Vidhi API Entry Point

This module exposes the FastAPI application instance `app`.
It is used by:
- uvicorn (local runs)
- console script entrypoint (vidhi-api)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.api.routes.health_routes import router as health_router
from src.api.routes.research_routes import router as research_router
from src.api.routes.document_routes import router as document_router
from src.api.routes.compliance_routes import router as compliance_router
from src.api.routes.feedback_routes import router as feedback_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Vidhi - Multi-Agent Legal Research and Drafting Assistant API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS setup (for Streamlit UI / external clients)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(research_router, prefix="/research", tags=["Research"])
    app.include_router(document_router, prefix="/documents", tags=["Documents"])
    app.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])
    app.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])

    return app


# FastAPI app instance (used by uvicorn + console entrypoint)
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

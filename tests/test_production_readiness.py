from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.middleware.security_headers import security_headers_middleware
from src.config.settings import get_settings


def test_settings_contract_exposes_runtime_fields():
    settings = get_settings()

    assert settings.APP_VERSION
    assert isinstance(settings.CORS_ALLOW_ORIGINS, tuple)
    assert isinstance(settings.ENABLE_API_DOCS, bool)
    assert settings.ENVIRONMENT in {"development", "staging", "production"}


def test_security_headers_middleware_sets_baseline_headers():
    app = FastAPI()
    app.middleware("http")(security_headers_middleware)

    @app.get('/ping')
    async def ping():
        return {"ok": True}

    client = TestClient(app)
    response = client.get('/ping')

    assert response.status_code == 200
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'

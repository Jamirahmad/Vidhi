from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.routes.system_routes import build_system_router


async def _health():
    return {
        "status": "ok",
        "provider": "openrouter",
        "model": "model",
        "apiKeyConfigured": True,
        "knowledge": {
            "provider": "langchain-chroma",
            "seedPath": "seed",
            "publicSource": "https://example.org",
            "available": True,
            "error": None,
        },
        "middleware": {
            "exceptionHandler": True,
            "requestLogger": True,
            "securityHeaders": True,
            "rateLimiter": {
                "enabled": True,
                "windowSeconds": 60,
                "maxRequests": 120,
                "bypassPaths": ["/api/v1/health"],
            },
        },
    }


async def _feedback_submit(payload):
    return {"status": "received", "feedbackId": payload.get("id", "1")}


async def _feedback_list(limit: int):
    return {"count": limit, "items": []}


def test_system_router_endpoints() -> None:
    app = FastAPI()
    app.include_router(
        build_system_router(
            health_handler=_health,
            feedback_submit_handler=_feedback_submit,
            feedback_list_handler=_feedback_list,
        )
    )

    client = TestClient(app)

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    submit = client.post("/api/v1/feedback", json={"id": "abc"})
    assert submit.status_code == 200
    assert submit.json()["feedbackId"] == "abc"

    listed = client.get("/api/v1/feedback", params={"limit": 3})
    assert listed.status_code == 200
    assert listed.json()["count"] == 3

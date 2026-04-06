from fastapi.testclient import TestClient

from backend.app.main import app


def test_queue_stats_contract_shape() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/queue/stats")
    assert response.status_code == 200

    payload = response.json()
    assert "timestamp" in payload
    assert "submitted" in payload
    assert "active" in payload
    assert "completed" in payload
    assert "failed" in payload

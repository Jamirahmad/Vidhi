from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_contract_shape():
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "middleware" in data
    assert "knowledge" in data

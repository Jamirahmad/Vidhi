import re

from fastapi.testclient import TestClient

from backend.app.main import app


SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def test_health_contract_shape():
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "appVersion" in data
    assert SEMVER_PATTERN.match(data["appVersion"])
    assert "middleware" in data
    assert "knowledge" in data

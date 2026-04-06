from fastapi.testclient import TestClient

from backend.app.main import app


def test_metrics_contract_shape() -> None:
    client = TestClient(app)

    # generate a couple of requests so metrics have non-zero values
    client.get("/api/v1/health")
    client.get("/api/v1/does-not-exist")

    response = client.get("/api/v1/metrics")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert "appVersion" in payload
    assert payload["totalRequests"] >= 2
    assert payload["totalErrors"] >= 1
    assert set(payload["statusBuckets"].keys()) >= {"2xx", "3xx", "4xx", "5xx"}
    assert isinstance(payload["routes"], dict)
    assert "/api/v1/health" in payload["routes"]

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_feedback_submit_and_list_contract() -> None:
    submit_response = client.post(
        "/api/v1/feedback",
        json={
            "screen": "issue-spotter",
            "rating": 5,
            "comment": "useful result",
        },
    )
    assert submit_response.status_code == 200
    submit_payload = submit_response.json()
    assert submit_payload["status"] == "received"
    assert "feedbackId" in submit_payload

    list_response = client.get("/api/v1/feedback", params={"limit": 5})
    assert list_response.status_code == 200

    list_payload = list_response.json()
    assert "count" in list_payload
    assert "items" in list_payload
    assert isinstance(list_payload["items"], list)
    assert any(item.get("id") == submit_payload["feedbackId"] for item in list_payload["items"])

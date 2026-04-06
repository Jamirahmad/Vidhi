from fastapi.testclient import TestClient

from backend.app.main import app


def test_prompt_versions_contract() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/prompts/versions")
    assert response.status_code == 200

    payload = response.json()
    assert "manifestVersion" in payload
    assert "systemPromptStackVersion" in payload
    assert "taskPromptVersions" in payload
    assert payload["taskPromptVersions"]["issue_spotter"] != "unversioned"

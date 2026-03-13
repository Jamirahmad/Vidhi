from src.core.api_orchestrator import Orchestrator


def test_research_orchestrator_returns_retrieval_metadata():
    orchestrator = Orchestrator()
    result = orchestrator.run_research(
        case_context="Consumer complaint delay and limitation issues",
        jurisdiction="India",
        case_type="consumer",
        user_constraints={"top_k": 3},
    )

    assert result["status"] == "SUCCESS"
    assert "retrieved_count" in result
    assert result["retrieved_count"] >= 0
    assert isinstance(result.get("precedents"), list)
    assert isinstance(result.get("issues"), list)


def test_research_api_message_includes_rag_flags(client):
    payload = {
        "request_id": "REQ-RAG-1",
        "jurisdiction": "India",
        "case_type": "consumer",
        "case_context": "Consumer complaint delay and limitation issues",
        "constraints": {"top_k": "3"},
    }

    response = client.post("/research/run", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert any(m.startswith("llm_used=") for m in data["messages"])
    assert any(m.startswith("retrieved_count=") for m in data["messages"])


# shared fixture compatible with existing test style
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)

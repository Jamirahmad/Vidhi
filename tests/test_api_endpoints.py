"""
API Endpoint Tests

These tests validate the public API contracts for the Legal Intelligence Platform.
They focus on:
- request/response structure
- status codes
- basic validation
- safety checks

Business logic and model accuracy are tested separately.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

# ---------------------------------------------------------------------
# NOTE:
# Replace `src.api.app` with the actual FastAPI app path
# ---------------------------------------------------------------------

try:
    from src.api.app import app  # type: ignore
except ImportError:
    app = None


# ---------------------------------------------------------------------
# Pytest Configuration
# ---------------------------------------------------------------------

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client():
    """
    Async test client for API requests.
    """
    if app is None:
        pytest.skip("API app not available for testing")

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------

async def test_health_check(client: AsyncClient):
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] in {"ok", "healthy"}


# ---------------------------------------------------------------------
# Case Intake API
# ---------------------------------------------------------------------

async def test_case_intake_success(client: AsyncClient):
    payload = {
        "case_title": "ABC Ltd vs Union of India",
        "court": "Supreme Court",
        "year": 2024,
        "summary": "Challenge to administrative action under Article 226.",
    }

    response = await client.post("/cases", json=payload)

    assert response.status_code in {200, 201}
    data = response.json()

    assert "case_id" in data
    assert isinstance(data["case_id"], str)


async def test_case_intake_validation_error(client: AsyncClient):
    payload = {
        "case_title": "",  # invalid
        "court": "Supreme Court",
    }

    response = await client.post("/cases", json=payload)

    assert response.status_code == 422


# ---------------------------------------------------------------------
# Research / Retrieval API
# ---------------------------------------------------------------------

async def test_research_query(client: AsyncClient):
    payload = {
        "query": "Applicability of Section 14 of the Limitation Act",
        "top_k": 5,
    }

    response = await client.post("/research/query", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert isinstance(data["results"], list)


async def test_research_query_empty(client: AsyncClient):
    payload = {"query": ""}

    response = await client.post("/research/query", json=payload)

    assert response.status_code == 422


# ---------------------------------------------------------------------
# Argument Builder API
# ---------------------------------------------------------------------

async def test_argument_builder(client: AsyncClient):
    payload = {
        "case_id": "SC-2024-1234",
        "issue": "Whether delay can be condoned under Section 14",
        "citations": [],
    }

    response = await client.post("/arguments/build", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "arguments" in data
    assert isinstance(data["arguments"], list)


# ---------------------------------------------------------------------
# Document Generation API
# ---------------------------------------------------------------------

async def test_document_generation(client: AsyncClient):
    payload = {
        "case_id": "SC-2024-1234",
        "document_type": "Research Note",
        "content": {
            "title": "Note on Section 14",
            "introduction": "Background of the dispute",
            "body": "Legal reasoning and analysis",
            "conclusion": "Findings and next steps",
        },
    }

    response = await client.post("/documents/generate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "document_text" in data
    assert isinstance(data["document_text"], str)


# ---------------------------------------------------------------------
# Compliance Check API
# ---------------------------------------------------------------------

async def test_compliance_check(client: AsyncClient):
    payload = {
        "content": "This argument relies on Section 14.",
        "citations": [],
        "content_type": "Argument Draft",
    }

    response = await client.post("/compliance/check", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "citation_coverage" in data
    assert "hallucination_risk" in data


# ---------------------------------------------------------------------
# Legal Aid API
# ---------------------------------------------------------------------

async def test_legal_aid_guidance(client: AsyncClient):
    payload = {
        "area_of_law": "Consumer Protection",
        "issue_description": "Delay in consumer forum proceedings",
    }

    response = await client.post("/legal-aid/guidance", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "overview" in data
    assert "possible_steps" in data
    assert isinstance(data["possible_steps"], list)


# ---------------------------------------------------------------------
# Security & Safety
# ---------------------------------------------------------------------

async def test_invalid_endpoint(client: AsyncClient):
    response = await client.get("/this-endpoint-does-not-exist")

    assert response.status_code == 404

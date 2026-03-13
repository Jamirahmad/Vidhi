"""Document generation API routes."""

from fastapi import APIRouter, Request, status

from src.agents.dga_document_generation_agent import DGADocumentGenerationAgent
from src.api.schemas.request_models import DocumentGenerationRequest
from src.api.schemas.response_models import DocumentGenerationResponse

router = APIRouter()


@router.post(
    "/generate",
    response_model=DocumentGenerationResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_document(request: Request, payload: DocumentGenerationRequest):
    agent = DGADocumentGenerationAgent()

    result = agent.run(
        {
            "request_id": payload.request_id,
            "jurisdiction": payload.jurisdiction,
            "document_type": payload.document_type,
            "case_description": payload.facts,
            "issues": {"primary_issues": [payload.case_type]},
            "compliance": {"disclaimer_required": True},
        }
    )

    data = result.get("data", {})

    return {
        "request_id": payload.request_id or getattr(request.state, "request_id", ""),
        "status": result.get("status", "FAILED"),
        "requires_human_review": True,
        "messages": ["DRAFT ONLY - lawyer review required"],
        "trace_id": None,
        "document_type": payload.document_type,
        "draft_text": data.get("draft_text", ""),
        "warnings": ["Auto-generated draft; verify facts, sections, and citations."],
    }

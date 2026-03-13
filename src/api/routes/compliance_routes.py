"""Compliance check API routes."""

from fastapi import APIRouter, Request, status

from src.agents.cca_compliance_check_agent import CCAComplianceCheckAgent
from src.api.schemas.request_models import ComplianceCheckRequest
from src.api.schemas.response_models import ComplianceCheckResponse

router = APIRouter()


@router.post(
    "/check",
    response_model=ComplianceCheckResponse,
    status_code=status.HTTP_200_OK,
)
async def run_compliance_check(request: Request, payload: ComplianceCheckRequest):
    agent = CCAComplianceCheckAgent()

    result = agent.run(
        {
            "document_text": payload.document_text,
            "jurisdiction": payload.jurisdiction,
            "document_type": payload.case_type,
        }
    )
    data = result.get("data", {})

    return {
        "request_id": payload.request_id or getattr(request.state, "request_id", ""),
        "status": result.get("status", "FAILED"),
        "requires_human_review": True,
        "messages": [data.get("notes", "Compliance review completed")],
        "trace_id": None,
        "compliance_passed": bool(data.get("can_generate_draft", False)),
        "findings": [
            {
                "type": "safety",
                "severity": "HIGH" if data.get("flagged_risks") else "LOW",
                "message": ", ".join(data.get("flagged_risks", [])) or "No major safety flags",
            }
        ],
    }

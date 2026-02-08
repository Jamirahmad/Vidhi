"""
Compliance Routes

Endpoints responsible for:
- Running compliance checks on drafted legal documents
- Validating filing requirements
- Enforcing human-in-the-loop escalation

Backed by:
- CCAComplianceCheckAgent
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.agents.cca_compliance_check_agent import CCAComplianceCheckAgent
from src.api.schemas.request_models import ComplianceCheckRequest
from src.api.schemas.response_models import ComplianceCheckResponse
from src.config.settings import get_settings

router = APIRouter()


@router.post(
    "/check",
    response_model=ComplianceCheckResponse,
    status_code=status.HTTP_200_OK,
)
async def run_compliance_check(
    request: Request,
    payload: ComplianceCheckRequest,
    settings=Depends(get_settings),
):
    """
    Run compliance checks on a generated legal document.

    This endpoint:
    - Validates procedural compliance (format, sections, annexures)
    - Flags missing mandatory components
    - Determines whether human review is mandatory
    """

    agent = CCAComplianceCheckAgent()

    try:
        result = agent.execute(
            document_text=payload.document_text,
            jurisdiction=payload.jurisdiction,
            case_type=payload.case_type,
            metadata=payload.metadata,
            request_id=getattr(request.state, "request_id", None),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compliance check failed due to internal error",
        ) from exc

    return {
        "request_id": getattr(request.state, "request_id", None),
        "agent": result["agent"],
        "status": result["status"],
        "compliance_issues": result["output"].get("issues"),
        "missing_requirements": result["output"].get("missing_requirements"),
        "is_compliant": result["output"].get("is_compliant"),
        "requires_human_review": result["requires_human_review"],
        "trace": result["trace"],
    }

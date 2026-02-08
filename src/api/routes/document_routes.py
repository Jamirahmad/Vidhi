"""
Document Routes

Endpoints responsible for:
- Generating draft legal documents (petitions, notices, affidavits, etc.)
- Enforcing human-in-the-loop review
- Returning traceable, auditable outputs

Backed by:
- DGADocumentGenerationAgent (DocComposer)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.agents.dga_document_generation_agent import DGADocumentGenerationAgent
from src.api.schemas.request_models import DocumentGenerationRequest
from src.api.schemas.response_models import DocumentGenerationResponse
from src.config.settings import get_settings

router = APIRouter()


@router.post(
    "/generate",
    response_model=DocumentGenerationResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_document(
    request: Request,
    payload: DocumentGenerationRequest,
    settings=Depends(get_settings),
):
    """
    Generate a draft legal document based on structured inputs.

    IMPORTANT:
    - Output is a DRAFT only
    - Human lawyer review is ALWAYS required
    """

    agent = DGADocumentGenerationAgent()

    try:
        result = agent.execute(
            case_facts=payload.case_facts,
            legal_issues=payload.legal_issues,
            arguments=payload.arguments,
            jurisdiction=payload.jurisdiction,
            case_type=payload.case_type,
            document_type=payload.document_type,
            language=payload.language,
            metadata=payload.metadata,
            request_id=getattr(request.state, "request_id", None),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document generation failed due to internal error",
        ) from exc

    return {
        "request_id": getattr(request.state, "request_id", None),
        "agent": result["agent"],
        "status": result["status"],
        "document_type": payload.document_type,
        "language": payload.language,
        "draft_text": result["output"].get("draft_text"),
        "citations": result["output"].get("citations"),
        "warnings": result["output"].get("warnings"),
        "requires_human_review": True,  # ALWAYS enforced at API layer
        "trace": result["trace"],
    }

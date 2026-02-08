"""
Research Routes

Handles legal research workflows:
- Case law search
- Issue identification
- Limitation analysis
- Structured research report generation

This route orchestrates multiple agents via the core orchestrator.
"""

from fastapi import APIRouter, Depends, status
from typing import Dict

from src.api.schemas.request_models import ResearchRequest
from src.api.schemas.response_models import ResearchResponse
from src.config.settings import get_settings
from src.core.orchestrator import Orchestrator
from src.core.response_formatter import format_research_response
from src.utils.time_utils import utc_now_iso

router = APIRouter()
settings = get_settings()


def get_orchestrator() -> Orchestrator:
    """
    Dependency injector for Orchestrator.
    Allows mocking during tests.
    """
    return Orchestrator()


@router.post(
    "/run",
    response_model=ResearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Run legal research workflow",
)
async def run_research(
    request: ResearchRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> Dict:
    """
    Executes the end-to-end legal research workflow.

    Agents involved:
    - CLSA: Case law search
    - LII: Issue identification
    - LAA: Limitation analysis
    - LRA: Legal research synthesis

    Output:
    - Structured research report
    - Citations
    - Human review flag
    """

    # ---- Orchestration ----
    orchestration_result = orchestrator.run_research(
        case_context=request.case_context,
        jurisdiction=request.jurisdiction,
        case_type=request.case_type,
        user_constraints=request.constraints,
    )

    # ---- Format response ----
    response_payload = format_research_response(
        orchestration_result=orchestration_result,
        request_id=request.request_id,
        generated_at=utc_now_iso(),
    )

    return response_payload

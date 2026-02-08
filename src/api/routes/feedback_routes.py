"""
Feedback Routes

Endpoints to:
- Collect structured user / lawyer feedback
- Associate feedback with request_id, agent, and output
- Support evaluation, governance, and future learning loops

NO model retraining happens here.
"""

from fastapi import APIRouter, HTTPException, Request, status
from typing import Optional
from datetime import datetime

from src.api.schemas.request_models import FeedbackRequest
from src.api.schemas.response_models import FeedbackResponse
from src.config.settings import get_settings
from src.utils.json_utils import safe_json_dump
from src.utils.time_utils import utc_now_iso
from src.storage.local_storage import LocalStorage

router = APIRouter()

storage = LocalStorage(base_path="outputs/feedback")


@router.post(
    "/submit",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_feedback(
    request: Request,
    payload: FeedbackRequest,
):
    """
    Submit feedback for a generated output.

    Feedback can be provided by:
    - Lawyer
    - Legal researcher
    - End user

    This data is used for:
    - Evaluation
    - Error analysis
    - Governance review
    """

    request_id = payload.request_id or getattr(request.state, "request_id", None)

    if not request_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="request_id is required to submit feedback",
        )

    feedback_record = {
        "request_id": request_id,
        "agent": payload.agent,
        "feedback_type": payload.feedback_type,
        "rating": payload.rating,
        "comments": payload.comments,
        "reviewer_role": payload.reviewer_role,
        "issues_flagged": payload.issues_flagged,
        "timestamp": utc_now_iso(),
    }

    try:
        storage.write_json(
            filename=f"{request_id}_feedback.json",
            data=feedback_record,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist feedback",
        ) from exc

    return {
        "status": "RECEIVED",
        "request_id": request_id,
        "message": "Feedback recorded successfully",
    }

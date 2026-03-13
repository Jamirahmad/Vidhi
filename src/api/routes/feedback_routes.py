"""Feedback collection routes."""

from fastapi import APIRouter, HTTPException, Request, status

from src.api.schemas.request_models import FeedbackRequest
from src.api.schemas.response_models import FeedbackResponse
from src.storage.local_storage import LocalStorage
from src.utils.json_utils import safe_json_dump
from src.utils.time_utils import utc_now_iso

router = APIRouter()
storage = LocalStorage(base_path="outputs/feedback")


@router.post(
    "/submit",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_feedback(request: Request, payload: FeedbackRequest):
    request_id = payload.request_id or getattr(request.state, "request_id", None)
    if not request_id:
        raise HTTPException(status_code=400, detail="request_id is required to submit feedback")

    feedback_record = {
        "request_id": request_id,
        "rating": payload.rating,
        "comments": payload.comments,
        "requires_followup": payload.requires_followup,
        "timestamp": utc_now_iso(),
    }

    try:
        storage.write_text(f"{request_id}_feedback.json", safe_json_dump(feedback_record))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Failed to persist feedback") from exc

    return {"status": "RECEIVED", "message": "Feedback recorded successfully"}

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from fastapi import APIRouter, Query

from backend.app.response_models import FeedbackListResponse, FeedbackSubmitResponse, HealthResponse


def build_system_router(
    health_handler: Callable[[], Awaitable[HealthResponse]],
    feedback_submit_handler: Callable[[Dict[str, Any]], Awaitable[FeedbackSubmitResponse]],
    feedback_list_handler: Callable[[int], Awaitable[FeedbackListResponse]],
) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["system"])

    @router.get("/health")
    async def health() -> HealthResponse:
        return await health_handler()

    @router.post("/feedback", response_model=FeedbackSubmitResponse)
    async def feedback_submit(payload: Dict[str, Any]) -> FeedbackSubmitResponse:
        return await feedback_submit_handler(payload)

    @router.get("/feedback", response_model=FeedbackListResponse)
    async def feedback_list(limit: int = Query(50, ge=1, le=200)) -> FeedbackListResponse:
        return await feedback_list_handler(limit)

    return router

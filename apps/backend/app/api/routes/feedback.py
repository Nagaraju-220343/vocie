import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.common import PaginatedResponse, Pagination
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])
service = FeedbackService()

@router.get("", response_model=PaginatedResponse[FeedbackResponse])
def get_feedback(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    callId: Optional[str] = None,
) -> PaginatedResponse[FeedbackResponse]:
    filters: dict = {}
    if callId: filters["callId"] = callId

    items, total = service.list_feedback(page, pageSize, filters)
    total_pages = math.ceil(total / pageSize) if pageSize else 0

    return PaginatedResponse(
        data=[FeedbackResponse(**item.model_dump()) for item in items],
        pagination=Pagination(page=page, pageSize=pageSize, total=total, totalPages=total_pages)
    )

@router.post("", response_model=FeedbackResponse, status_code=201)
def create_feedback(feedback: FeedbackCreate) -> FeedbackResponse:
    created = service.create_feedback(feedback)
    if not created:
        raise HTTPException(status_code=500, detail={"error": {"code": "INTERNAL_ERROR", "message": "Failed to create feedback"}})
    return FeedbackResponse(**created.model_dump())

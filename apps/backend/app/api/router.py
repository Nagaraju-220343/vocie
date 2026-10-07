from fastapi import APIRouter

from app.api.routes.calls import router as calls_router
from app.api.routes.orders import router as orders_router
from app.api.routes.customers import router as customers_router
from app.api.routes.faqs import router as faqs_router
from app.api.routes.feedback import router as feedback_router
from app.services.feedback_service import FeedbackService
from app.schemas.feedback import FeedbackResponse
from typing import List

api_router = APIRouter()

api_router.include_router(calls_router)
api_router.include_router(orders_router)
api_router.include_router(customers_router)
api_router.include_router(faqs_router)
api_router.include_router(feedback_router)

# Extra endpoint for call specific feedback
@api_router.get("/calls/{call_id}/feedback", response_model=List[FeedbackResponse], tags=["Feedback"])
def get_call_feedback(call_id: str):
    service = FeedbackService()
    items = service.list_feedback_by_call(call_id)
    return [FeedbackResponse(**item.model_dump()) for item in items]

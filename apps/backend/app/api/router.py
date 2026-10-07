from typing import List

from fastapi import APIRouter

from app.api.routes.calls import router as calls_router
from app.api.routes.customers import router as customers_router
from app.api.routes.faqs import router as faqs_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.voice import router as voice_router
from app.schemas.feedback import FeedbackResponse
from app.services.feedback_service import FeedbackService

api_router = APIRouter()

api_router.include_router(health_router)

api_router.include_router(calls_router)
api_router.include_router(orders_router)
api_router.include_router(customers_router)
api_router.include_router(faqs_router)
api_router.include_router(feedback_router)
api_router.include_router(voice_router)
from app.api.routes.webhooks import router as webhooks_router
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

from app.api.routes.demo import router as demo_router
api_router.include_router(demo_router)
# Extra endpoint for call specific feedback
@api_router.get("/calls/{call_id}/feedback", response_model=List[FeedbackResponse], tags=["Feedback"])
def get_call_feedback(call_id: str) -> List[FeedbackResponse]:
    service = FeedbackService()
    items = service.list_feedback_by_call(call_id)
    return [FeedbackResponse(**item.model_dump()) for item in items]

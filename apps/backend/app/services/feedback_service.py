from typing import List, Optional, Tuple

from app.models.feedback import FeedbackModel
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate


class FeedbackService:
    def __init__(self, repository: Optional[FeedbackRepository] = None):
        self.repository = repository or FeedbackRepository()

    def get_feedback(self, feedback_id: str) -> Optional[FeedbackModel]:
        return self.repository.get_by_id(feedback_id)

    def list_feedback(self, page: int, page_size: int, filters: dict) -> Tuple[List[FeedbackModel], int]:
        skip = (page - 1) * page_size
        items = self.repository.list(limit=page_size, skip=skip, filters=filters)
        total = self.repository.count(filters=filters)
        return items, total

    def create_feedback(self, feedback_data: FeedbackCreate) -> Optional[FeedbackModel]:
        feedback_model = FeedbackModel(**feedback_data.model_dump())
        feedback_id = self.repository.create(feedback_model)
        return self.repository.get_by_id(feedback_id)

    def list_feedback_by_call(self, call_id: str) -> List[FeedbackModel]:
        # Using the base list method with filters and high page size
        items = self.repository.list(limit=1000, skip=0, filters={"callId": call_id})
        return items

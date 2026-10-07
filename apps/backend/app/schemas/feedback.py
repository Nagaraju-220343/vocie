from datetime import datetime
from pydantic import BaseModel

class FeedbackBase(BaseModel):
    callId: str
    field: str
    originalValue: str | None = None
    correctedValue: str | None = None
    reason: str | None = None
    createdBy: str = "system"

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: str
    createdAt: datetime

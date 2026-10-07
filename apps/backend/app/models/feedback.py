from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackModel(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    callId: str
    field: str
    originalValue: str | None = None
    correctedValue: str | None = None
    reason: str | None = None
    createdBy: str = "system"
    createdAt: datetime = Field(default_factory=datetime.utcnow)

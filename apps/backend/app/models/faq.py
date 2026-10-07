from datetime import datetime

from pydantic import BaseModel, Field


class FaqModel(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    question: str
    answerFr: str
    answerEn: str
    category: str
    active: bool = True
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

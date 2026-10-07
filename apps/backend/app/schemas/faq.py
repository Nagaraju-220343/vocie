from datetime import datetime
from pydantic import BaseModel

class FaqBase(BaseModel):
    question: str
    answerFr: str
    answerEn: str
    category: str
    active: bool = True

class FaqCreate(FaqBase):
    pass

class FaqUpdate(BaseModel):
    question: str | None = None
    answerFr: str | None = None
    answerEn: str | None = None
    category: str | None = None
    active: bool | None = None

class FaqResponse(FaqBase):
    id: str
    updatedAt: datetime

class FaqMatchResponse(BaseModel):
    matched: bool
    faq: FaqResponse | None = None
    answer: str | None = None

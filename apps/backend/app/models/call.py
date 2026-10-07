from datetime import datetime

from pydantic import BaseModel, Field


class CallModel(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    providerCallId: str
    direction: str
    fromNumber: str
    toNumber: str
    language: str
    intent: str
    status: str
    startedAt: datetime | None = None
    endedAt: datetime | None = None
    durationSeconds: int = 0
    transcript: str = ""
    summary: str = ""
    recordingUrl: str | None = None
    escalated: bool = False
    escalationReason: str | None = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

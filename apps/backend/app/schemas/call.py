from datetime import datetime
from pydantic import BaseModel, Field

class CallBase(BaseModel):
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

class CallCreate(CallBase):
    providerCallId: str

class CallUpdate(BaseModel):
    status: str | None = None
    language: str | None = None
    intent: str | None = None
    endedAt: datetime | None = None
    durationSeconds: int | None = None
    transcript: str | None = None
    summary: str | None = None
    recordingUrl: str | None = None
    escalated: bool | None = None
    escalationReason: str | None = None

class CallResponse(CallBase):
    id: str
    providerCallId: str
    createdAt: datetime
    updatedAt: datetime

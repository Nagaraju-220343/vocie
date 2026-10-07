from pydantic import BaseModel
from typing import Optional

class EscalationRequest(BaseModel):
    reason: str
    notes: Optional[str] = None

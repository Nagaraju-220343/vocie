from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TranscriptMessage(BaseModel):
    speaker: str
    text: str
    language: str = "unknown"
    timestamp: Optional[datetime] = None
    sequence: int = 0

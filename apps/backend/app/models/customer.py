from datetime import datetime

from pydantic import BaseModel, Field


class CustomerModel(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    name: str | None = None
    phone: str
    address: str | None = None
    callCount: int = 0
    lastCallAt: datetime | None = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

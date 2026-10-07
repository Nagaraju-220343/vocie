from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class OrderItemModel(BaseModel):
    name: str
    quantity: int
    price: float | None = None

class OrderModel(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    callId: str
    customerId: str | None = None
    items: List[OrderItemModel] = Field(default_factory=list)
    customerName: str | None = None
    phone: str | None = None
    address: str | None = None
    orderType: str = "UNKNOWN"
    status: str = "PENDING"
    notes: str = ""
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

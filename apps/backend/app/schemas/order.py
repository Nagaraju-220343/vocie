from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float | None = None

class OrderBase(BaseModel):
    callId: str
    customerId: str | None = None
    customerName: str | None = None
    phone: str | None = None
    address: str | None = None
    orderType: str = "UNKNOWN"
    status: str = "PENDING"
    notes: str = ""
    items: List[OrderItem] = Field(default_factory=list)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    items: List[OrderItem] | None = None
    address: str | None = None
    orderType: str | None = None
    status: str | None = None
    notes: str | None = None

class OrderResponse(OrderBase):
    id: str
    createdAt: datetime
    updatedAt: datetime

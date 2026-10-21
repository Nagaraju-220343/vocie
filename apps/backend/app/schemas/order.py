from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float | None = None
    size: str | None = None
    crust: str | None = None
    options: List[str] = Field(default_factory=list)

class OrderBase(BaseModel):
    callId: str
    customerId: str | None = None
    customerName: str | None = None
    phone: str | None = None
    address: str | None = None
    orderType: str = "UNKNOWN"
    status: str = "PENDING"
    notes: str = ""
    restaurant: str = "le_gourmet"
    source: str = "voice_agent"
    items: List[OrderItem] = Field(default_factory=list)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    items: List[OrderItem] | None = None
    address: str | None = None
    orderType: str | None = None
    status: str | None = None
    notes: str | None = None
    customerName: str | None = None
    phone: str | None = None
    restaurant: str | None = None
    source: str | None = None

class OrderResponse(OrderBase):
    id: str
    success: bool = True
    order_id: str | None = None
    message: str | None = None
    createdAt: datetime
    updatedAt: datetime

    def model_post_init(self, __context: object) -> None:
        if not self.order_id and self.id:
            self.order_id = self.id

class OrderActionResponse(BaseModel):
    success: bool
    order_id: str | None = None
    status: str | None = None
    message: str | None = None
    error: str | None = None
    order: OrderResponse | None = None

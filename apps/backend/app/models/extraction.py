from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.order import OrderItemModel


class OrderExtractionResult(BaseModel):
    intent: str
    language: str = "unknown"
    customerName: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    fulfillmentType: Optional[str] = None
    items: List[OrderItemModel] = Field(default_factory=list)
    confidence: float = 1.0
    validationStatus: str = "VALID"
    missingFields: List[str] = Field(default_factory=list)

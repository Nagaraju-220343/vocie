from datetime import datetime
from pydantic import BaseModel, Field

class CustomerBase(BaseModel):
    name: str | None = None
    phone: str
    address: str | None = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None

class CustomerResponse(CustomerBase):
    id: str
    callCount: int
    lastCallAt: datetime | None = None
    createdAt: datetime
    updatedAt: datetime

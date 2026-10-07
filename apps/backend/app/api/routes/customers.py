import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.common import ErrorResponse, PaginatedResponse, Pagination
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])
service = CustomerService()

@router.get("", response_model=PaginatedResponse[CustomerResponse])
def get_customers(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    phone: Optional[str] = None,
) -> PaginatedResponse[CustomerResponse]:
    filters: dict = {}
    if phone: filters["phone"] = phone

    items, total = service.list_customers(page, pageSize, filters)
    total_pages = math.ceil(total / pageSize) if pageSize else 0

    return PaginatedResponse(
        data=[CustomerResponse(**item.model_dump()) for item in items],
        pagination=Pagination(page=page, pageSize=pageSize, total=total, totalPages=total_pages)
    )

@router.get("/{customer_id}", response_model=CustomerResponse, responses={404: {"model": ErrorResponse}})
def get_customer(customer_id: str) -> CustomerResponse:
    customer = service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Customer not found"}})
    return CustomerResponse(**customer.model_dump())

@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate) -> CustomerResponse:
    created = service.create_customer(customer)
    if not created:
        raise HTTPException(status_code=500, detail={"error": {"code": "INTERNAL_ERROR", "message": "Failed to create customer"}})
    return CustomerResponse(**created.model_dump())

@router.patch("/{customer_id}", response_model=CustomerResponse, responses={404: {"model": ErrorResponse}})
def update_customer(customer_id: str, updates: CustomerUpdate) -> CustomerResponse:
    updated = service.update_customer(customer_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Customer not found"}})
    return CustomerResponse(**updated.model_dump())

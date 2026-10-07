from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.schemas.common import PaginatedResponse, Pagination, ErrorResponse, ErrorDetail
from app.services.order_service import OrderService
import math

router = APIRouter(prefix="/orders", tags=["Orders"])
service = OrderService()

@router.get("", response_model=PaginatedResponse[OrderResponse])
def get_orders(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    customerId: Optional[str] = None,
    callId: Optional[str] = None,
) -> PaginatedResponse[OrderResponse]:
    filters: dict = {}
    if status: filters["status"] = status
    if customerId: filters["customerId"] = customerId
    if callId: filters["callId"] = callId

    items, total = service.list_orders(page, pageSize, filters)
    total_pages = math.ceil(total / pageSize) if pageSize else 0

    return PaginatedResponse(
        data=[OrderResponse(**item.model_dump()) for item in items],
        pagination=Pagination(page=page, pageSize=pageSize, total=total, totalPages=total_pages)
    )

@router.get("/{order_id}", response_model=OrderResponse, responses={404: {"model": ErrorResponse}})
def get_order(order_id: str) -> OrderResponse:
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Order not found"}})
    return OrderResponse(**order.model_dump())

@router.post("", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate) -> OrderResponse:
    created = service.create_order(order)
    if not created:
        raise HTTPException(status_code=500, detail={"error": {"code": "INTERNAL_ERROR", "message": "Failed to create order"}})
    return OrderResponse(**created.model_dump())

@router.patch("/{order_id}", response_model=OrderResponse, responses={404: {"model": ErrorResponse}})
def update_order(order_id: str, updates: OrderUpdate) -> OrderResponse:
    updated = service.update_order(order_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Order not found"}})
    return OrderResponse(**updated.model_dump())

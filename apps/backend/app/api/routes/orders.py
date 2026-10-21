import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

import logging
from app.schemas.common import ErrorResponse, PaginatedResponse, Pagination
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)

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
    if callId:
        from bson.objectid import ObjectId
        if ObjectId.is_valid(callId):
            from app.repositories.call_repository import CallRepository
            call = CallRepository().get_by_id(callId)
            filters["callId"] = call.providerCallId if call else callId
        else:
            filters["callId"] = callId

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

@router.patch("/{order_id}", response_model=OrderResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def update_order(order_id: str, request: Request) -> OrderResponse:
    from app.realtime.socket import publisher
    from app.graph.workflow import live_state_service
    from bson.objectid import ObjectId

    # Parse raw JSON to support both flat parameters (args_at_root=True) and nested {"args": {...}} (args_at_root=False)
    try:
        raw_body = await request.json()
    except Exception:
        raw_body = {}

    if isinstance(raw_body, dict) and "args" in raw_body and isinstance(raw_body["args"], dict):
        payload_dict = raw_body["args"]
    else:
        payload_dict = raw_body if isinstance(raw_body, dict) else {}

    try:
        updates = OrderUpdate(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": {"code": "VALIDATION_ERROR", "message": str(e)}})
    
    # Check if order_id is a call_id. If so, invoke graph.
    if not ObjectId.is_valid(order_id):
        if order_id in ["{{call.call_id}}", "{{call_id}}"]:
            from app.repositories.call_repository import CallRepository
            calls = CallRepository().list(filters={"status": "IN_PROGRESS"}, limit=1)
            if calls:
                order_id = calls[0].providerCallId
        logger.info(f"[DIAGNOSTIC] Order Update | Provider Call ID: {order_id}")
        
        # Validate items before dispatching
        if updates.items is not None:
            if len(updates.items) == 0:
                raise HTTPException(status_code=400, detail={"error": {"code": "VALIDATION_ERROR", "message": "Order items cannot be empty"}})
            for itm in updates.items:
                if not itm.name or not itm.name.strip():
                    raise HTTPException(status_code=400, detail={"error": {"code": "VALIDATION_ERROR", "message": "Item name cannot be empty"}})
                if itm.quantity <= 0:
                    raise HTTPException(status_code=400, detail={"error": {"code": "VALIDATION_ERROR", "message": f"Invalid quantity ({itm.quantity}) for item {itm.name}"}})
        
        # Route through live state workflow
        state_update = {"order": updates.model_dump(exclude_unset=True)}
        live_state_service.process_event(order_id, state_update, "update_order")
        updated, error = service.update_order(order_id, updates)
    else:
        updated, error = service.update_order(order_id, updates)
        
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": error}})
        raise HTTPException(status_code=400, detail={"error": {"code": "VALIDATION_ERROR", "message": error}})

    if not updated or not updated.id:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": {"code": "PERSISTENCE_ERROR", "message": "Draft order could not be saved to database"}}
        )
        
    await publisher.publish("order.updated", updated.callId, 0, updated.model_dump(mode='json'))
    resp_dict = updated.model_dump()
    resp_dict["success"] = True
    # If this is a draft update, return "draft_saved" for Retell agent contract
    if updated.status in ["DRAFT", "PENDING"]:
        resp_dict["status"] = "draft_saved"
    resp_dict["order_id"] = str(updated.id)
    resp_dict["message"] = "Order draft saved successfully"
    return OrderResponse(**resp_dict)

@router.post("/{order_id}/confirm", response_model=OrderResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def confirm_order(order_id: str) -> OrderResponse:
    from app.realtime.socket import publisher
    from app.graph.workflow import live_state_service
    from bson.objectid import ObjectId
    
    # Resolve call template placeholder if present
    if not ObjectId.is_valid(order_id):
        if order_id in ["{{call.call_id}}", "{{call_id}}"]:
            from app.repositories.call_repository import CallRepository
            calls = CallRepository().list(filters={"status": "IN_PROGRESS"}, limit=1)
            if calls:
                order_id = calls[0].providerCallId

        # Process through workflow validation
        live_state_service.process_event(order_id, {}, "update_order")

    order, error, is_duplicate = service.confirm_order(order_id)
    if error:
        if "does not exist" in error.lower() or "not found" in error.lower():
            raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "RESOURCE_NOT_FOUND", "message": error}})
        raise HTTPException(status_code=400, detail={"success": False, "error": {"code": "VALIDATION_ERROR", "message": error}})
        
    if order and order.id:
        await publisher.publish("order.updated", order.callId, 0, order.model_dump(mode='json'))
        resp_dict = order.model_dump()
        resp_dict["success"] = True
        resp_dict["status"] = "confirmed"
        resp_dict["order_id"] = str(order.id)
        resp_dict["message"] = "Order confirmed successfully"
        return OrderResponse(**resp_dict)
        
    raise HTTPException(status_code=500, detail={"success": False, "error": {"code": "PERSISTENCE_ERROR", "message": "Order could not be saved or confirmed in database"}})

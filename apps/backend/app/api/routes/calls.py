import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.call import CallCreate, CallResponse, CallUpdate
from app.schemas.common import ErrorResponse, PaginatedResponse, Pagination
from app.services.call_service import CallService

router = APIRouter(prefix="/calls", tags=["Calls"])
service = CallService()

@router.get("", response_model=PaginatedResponse[CallResponse])
def get_calls(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    intent: Optional[str] = None,
    language: Optional[str] = None,
    direction: Optional[str] = None,
) -> PaginatedResponse[CallResponse]:
    filters: dict = {}
    if status: filters["status"] = status
    if intent: filters["intent"] = intent
    if language: filters["language"] = language
    if direction: filters["direction"] = direction

    items, total = service.list_calls(page, pageSize, filters)
    total_pages = math.ceil(total / pageSize) if pageSize else 0

    return PaginatedResponse(
        data=[CallResponse(**item.model_dump()) for item in items],
        pagination=Pagination(page=page, pageSize=pageSize, total=total, totalPages=total_pages)
    )

@router.get("/{call_id}", response_model=CallResponse, responses={404: {"model": ErrorResponse}})
def get_call(call_id: str) -> CallResponse:
    call = service.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Call not found"}})
    return CallResponse(**call.model_dump())

@router.post("", response_model=CallResponse, status_code=201, responses={409: {"model": ErrorResponse}})
def create_call(call: CallCreate) -> CallResponse:
    created = service.create_call(call)
    if not created:
        raise HTTPException(status_code=409, detail={"error": {"code": "DUPLICATE_RESOURCE", "message": "Provider call ID already exists"}})
    return CallResponse(**created.model_dump())

@router.patch("/{call_id}", response_model=CallResponse, responses={404: {"model": ErrorResponse}})
def update_call(call_id: str, updates: CallUpdate) -> CallResponse:
    updated = service.update_call(call_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Call not found"}})
    return CallResponse(**updated.model_dump())

from app.schemas.escalation import EscalationRequest
from app.services.escalation_service import EscalationService

@router.post("/{call_id}/escalate", response_model=CallResponse, responses={404: {"model": ErrorResponse}})
def escalate_call(call_id: str, request: EscalationRequest) -> CallResponse:
    from app.graph.workflow import live_state_service
    from bson.objectid import ObjectId
    
    # Process through LangGraph first
    state_update = {"escalation": {"reason": request.reason, "notes": request.notes}}
    live_state_service.process_event(call_id, state_update, "handle_escalation")
    
    # The LangGraph node calls EscalationService which handles DB + socket
    if ObjectId.is_valid(call_id):
        updated = service.get_call(call_id)
    else:
        updated = service.repository.get_by_provider_call_id(call_id)
        
    if not updated:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Call not found"}})
    return CallResponse(**updated.model_dump())

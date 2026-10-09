from typing import Any
import logging
from app.graph.state import CallState
from app.services.call_service import CallService
from app.services.order_service import OrderService
from app.services.escalation_service import EscalationService
from app.schemas.order import OrderUpdate, OrderCreate

logger = logging.getLogger(__name__)

call_service = CallService()
order_service = OrderService()
escalation_service = EscalationService()

def update_call_state(state: CallState) -> dict:
    if state.get("call_id"):
        try:
            # We don't overwrite if it already exists, or we just sync
            # To keep it simple, we don't aggressively write to Mongo here unless needed.
            # But we could update status.
            pass
        except Exception as e:
            logger.error(f"Error updating call state: {e}")
    return {"status": state.get("status", "IN_PROGRESS")}

def update_transcript(state: CallState) -> dict:
    return {}

def update_order(state: CallState) -> dict:
    order_data = state.get("order")
    call_id = state.get("provider_call_id") or state.get("call_id")
    
    if not order_data or not call_id:
        return {}
        
    try:
        # We need to map order_data to OrderUpdate schema
        updates = OrderUpdate(**order_data)
        # Use existing OrderService update flow (which handles live draft auto-creation)
        updated = order_service.update_order(call_id, updates)
        if updated:
            return {"order": updated.model_dump(mode="json")}
    except Exception as e:
        logger.error(f"Error in update_order node: {e}")
    
    return {}

def validate_order(state: CallState) -> dict:
    # Just validate order contents
    order_data = state.get("order")
    if not order_data:
        return {"order_validation_status": "INVALID"}
        
    items = order_data.get("items", [])
    if not items:
        return {"order_validation_status": "INVALID"}
        
    for item in items:
        if item.get("quantity", 0) <= 0:
            return {"order_validation_status": "INVALID"}
            
    if not order_data.get("customerName") and not order_data.get("phone"):
        return {"order_validation_status": "INVALID"}
        
    if order_data.get("orderType") == "DELIVERY" and not order_data.get("address"):
        return {"order_validation_status": "INVALID"}
        
    return {"order_validation_status": "VALID"}

def handle_escalation(state: CallState) -> dict:
    escalation_data = state.get("escalation")
    call_id = state.get("provider_call_id") or state.get("call_id")
    
    if not escalation_data or not call_id:
        return {}
        
    try:
        reason = escalation_data.get("reason", "Unknown")
        notes = escalation_data.get("notes")
        escalation_service.escalate_call(call_id, reason, notes)
    except Exception as e:
        logger.error(f"Error in handle_escalation node: {e}")
        
    return {}


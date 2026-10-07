import logging
import asyncio
from typing import Optional
from app.repositories.call_repository import CallRepository
from app.models.call import CallModel
from app.schemas.call import CallUpdate
from app.realtime.socket import publisher

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self):
        self.call_repo = CallRepository()

    def escalate_call(self, call_id: str, reason: str, notes: Optional[str] = None) -> Optional[CallModel]:
        # Fetch call
        call = self.call_repo.get_by_id(call_id)
        if not call:
            return None
            
        # Update call state
        updates = {
            "status": "ESCALATED",
            "escalationReason": reason,
        }
        
        # Merge dictionary using standard approach
        success = self.call_repo.update(call_id, updates)
        if not success:
            return None
            
        # Get updated call
        updated_call = self.call_repo.get_by_id(call_id)
        if updated_call:
            # Publish event async without blocking
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(
                    publisher.publish("call.escalated", updated_call.id, 999, {"reason": reason, "status": "ESCALATED"})
                )
            except Exception as e:
                logger.error(f"Failed to publish escalation event: {e}")
                
        return updated_call

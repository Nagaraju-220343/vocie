import logging
import asyncio
from typing import Optional
from app.repositories.call_repository import CallRepository
from app.models.call import CallModel
from app.schemas.call import CallUpdate
from app.realtime.socket import publisher

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self) -> None:
        self.call_repo = CallRepository()

    def escalate_call(self, call_id: str, reason: str, notes: Optional[str] = None) -> Optional[CallModel]:
        # Fetch call
        from bson.objectid import ObjectId
        if ObjectId.is_valid(call_id):
            call = self.call_repo.get_by_id(call_id)
        else:
            call = self.call_repo.get_by_provider_call_id(call_id)
            
        if not call:
            if not ObjectId.is_valid(call_id):
                # Auto-create missing call to handle delayed webhooks
                new_call = CallModel(
                    providerCallId=call_id,
                    direction="inbound",
                    fromNumber="unknown",
                    toNumber="unknown",
                    language="unknown",
                    intent="UNKNOWN",
                    status="IN_PROGRESS"
                )
                db_id = self.call_repo.create(new_call)
            else:
                return None
        else:
            db_id = str(call.id)
            
        # Update call state
        updates = {
            "status": "ESCALATED",
            "escalated": True,
            "escalationReason": reason,
        }
        logger.info(f"[DIAGNOSTIC] Escalation | DB ID: {db_id} | Reason: {reason}")
        
        # Merge dictionary using standard approach with the real DB ID
        success = self.call_repo.update(db_id, updates)
        if not success:
            return None
            
        # Get updated call
        updated_call = self.call_repo.get_by_id(db_id)
        if updated_call:
            # Publish event async without blocking
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(
                    publisher.publish("call.escalated", db_id, 999, {
                        "reason": reason, 
                        "status": "ESCALATED",
                        "escalated": True
                    })
                )
            except Exception as e:
                logger.error(f"Failed to publish escalation event: {e}")
                
        return updated_call

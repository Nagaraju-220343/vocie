import logging
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, Request

from app.integrations.retell.webhooks.adapter import RetellWebhookAdapter
from app.models.transcript import TranscriptMessage
from app.repositories.call_repository import CallRepository
from app.services.call_completion_service import CallCompletionService

logger = logging.getLogger(__name__)

router = APIRouter()
adapter = RetellWebhookAdapter()
call_completion = CallCompletionService()
call_repo = CallRepository()

@router.post("/retell")
async def retell_webhook(
    request: Request,
    x_retell_signature: str = Header(None)
) -> Dict[str, Any]:
    if not x_retell_signature:
        logger.warning("Missing Retell signature")
        raise HTTPException(status_code=401, detail="Missing signature")
        
    payload_bytes = await request.body()
    
    if not adapter.verify_signature(x_retell_signature, payload_bytes):
        logger.warning("Invalid Retell signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    event = payload.get("event")
    call_data = payload.get("call", {})
    provider_call_id = call_data.get("call_id")
    
    if not provider_call_id:
        logger.error("Missing call_id in webhook payload")
        return {"status": "ignored", "reason": "missing call_id"}
        
    logger.info(f"Received webhook event {event} for call {provider_call_id}")
    
    if event in ["call_started", "call_analyzed"]:
        # We can update the call status
        call = call_completion._get_or_create_call(provider_call_id)
        if event == "call_started":
            call_repo.update(str(call.id), {"status": "IN_PROGRESS"})
            
    elif event == "call_ended":
        transcript_data = call_data.get("transcript", [])
        
        # Convert Retell transcript objects to internal model
        messages = []
        for index, item in enumerate(transcript_data):
            # Retell format uses 'role' and 'content'
            speaker = "customer" if item.get("role") == "user" else "agent"
            text = item.get("content", "")
            messages.append(TranscriptMessage(speaker=speaker, text=text, sequence=index))
            
        call = call_completion._get_or_create_call(provider_call_id)
        
        # We just store everything since this is final transcript
        call.transcriptMessages = [m.model_dump() for m in messages]
        call_repo.update(str(call.id), {"transcriptMessages": call.transcriptMessages})
        
        call_completion.process_completed_call(provider_call_id, messages)

    return {"status": "success"}

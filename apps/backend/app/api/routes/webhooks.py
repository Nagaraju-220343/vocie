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
        
    logger.info(f"[DIAGNOSTIC] Webhook Event: {event} | Provider Call ID: {provider_call_id}")
    
    from app.graph.workflow import live_state_service
    
    try:
        if event == "call_started":
            call = call_completion._get_or_create_call(provider_call_id)
            try:
                state_update = {"status": "IN_PROGRESS"}
                live_state_service.process_event(provider_call_id, state_update, "update_call_state")
            except Exception as e:
                logger.warning(f"LiveStateService call_started error (non-fatal): {e}")
                
            if call and call.id:
                call_repo.update(str(call.id), {"status": "IN_PROGRESS"})
        
            # Emit real-time event to notify frontend instantly of active call
            from app.realtime.socket import publisher
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            loop.create_task(publisher.publish("call.started", provider_call_id, 0, {
                "status": "IN_PROGRESS",
                "callId": str(call.id),
                "providerCallId": provider_call_id
            }))
            
        elif event == "call_analyzed":
            call = call_completion._get_or_create_call(provider_call_id)
            state_update = {"status": "ANALYZED"}
            live_state_service.process_event(provider_call_id, state_update, "update_call_state")
            call_completion.process_call_analysis(provider_call_id, call_data)
            
        elif event == "call_ended":
            transcript_data = call_data.get("transcript_object")
            if not transcript_data and isinstance(call_data.get("transcript"), list):
                transcript_data = call_data.get("transcript")
            elif not transcript_data:
                transcript_data = []
            
            # Convert Retell transcript objects to internal model
            messages = []
            for index, item in enumerate(transcript_data):
                speaker = "customer" if item.get("role") == "user" else "agent"
                text = item.get("content", "")
                messages.append(TranscriptMessage(speaker=speaker, text=text, sequence=index))
                
            call = call_completion._get_or_create_call(provider_call_id)
            if call and call.id:
                # We just store everything since this is final transcript
                transcript_str = "\n\n".join([f"{m.speaker.upper()}:\n{m.text}" for m in messages])
                call.transcript = transcript_str
                call.transcriptMessages = [m.model_dump() for m in messages]
                
                # Load existing graph state and update it
                state_update = {
                    "status": "COMPLETED",
                    "transcript": call.transcriptMessages
                }
                live_state_service.process_event(provider_call_id, state_update, "update_transcript")
                
                call_repo.update(str(call.id), {
                    "transcriptMessages": call.transcriptMessages,
                    "transcript": transcript_str,
                    "status": "COMPLETED"
                })
            call_completion.process_completed_call(provider_call_id, messages, retell_call_data=call_data)
            
            # Emit real-time events to update the frontend instantly
            from app.realtime.socket import publisher
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            loop.create_task(publisher.publish("transcript.updated", provider_call_id, 0, {
                "role": "system",
                "content": "Final transcript processed."
            }))
            loop.create_task(publisher.publish("call.ended", provider_call_id, 0, {
                "status": "COMPLETED"
            }))
    except Exception as e:
        logger.error(f"Error handling webhook event {event}: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

    return {"status": "success"}

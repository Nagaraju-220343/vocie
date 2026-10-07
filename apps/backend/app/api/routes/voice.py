from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.providers.voice.base import VoiceProviderError
from app.providers.voice.factory import get_voice_provider

router = APIRouter(prefix="/voice", tags=["Voice"])

class OutboundCallRequest(BaseModel):
    phone_number: str
    metadata: Optional[Dict[str, Any]] = None

class OutboundCallResponse(BaseModel):
    provider: str
    provider_call_id: str
    status: str

@router.post("/outbound", response_model=OutboundCallResponse, status_code=201)
async def create_outbound_call(request: OutboundCallRequest) -> OutboundCallResponse:
    """
    Development endpoint for manually triggering an outbound test call.
    """
    provider = get_voice_provider()
    try:
        result = await provider.create_outbound_call(
            to_number=request.phone_number,
            metadata=request.metadata
        )
        return OutboundCallResponse(
            provider=result.provider,
            provider_call_id=result.provider_call_id,
            status=result.status
        )
    except VoiceProviderError as e:
        raise HTTPException(status_code=500, detail={"error": {"code": "PROVIDER_ERROR", "message": str(e)}})

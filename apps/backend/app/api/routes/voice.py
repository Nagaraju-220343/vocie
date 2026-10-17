import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.config.settings import settings
from app.models.call import CallModel
from app.providers.voice.base import VoiceProviderError
from app.providers.voice.factory import get_voice_provider
from app.repositories.call_repository import CallRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])


class OutboundCallRequest(BaseModel):
    phone_number: str
    metadata: Optional[Dict[str, Any]] = None


class OutboundCallResponse(BaseModel):
    provider: str
    provider_call_id: str
    status: str


class WebCallRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    dynamic_variables: Optional[Dict[str, Any]] = None


class WebCallResponse(BaseModel):
    provider: str
    call_id: str
    access_token: str
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


@router.post("/web-call", response_model=WebCallResponse, status_code=201)
async def create_web_call(request: Optional[WebCallRequest] = None) -> WebCallResponse:
    """
    Initiates a browser-based web call with the configured Retell AI agent.
    Returns the provider call_id and a temporary access_token for the Web SDK.
    Never exposes the Retell API key or sensitive credentials.
    """
    # 1. Validate configuration
    if not settings.retell_api_key:
        logger.error("Web call failed: RETELL_API_KEY is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "CONFIGURATION_ERROR", "message": "Voice service credentials are not configured"}}
        )

    if not settings.retell_agent_id:
        logger.error("Web call failed: RETELL_AGENT_ID is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "CONFIGURATION_ERROR", "message": "Voice agent is not configured"}}
        )

    metadata = request.metadata if request else None
    dynamic_variables = request.dynamic_variables if request else None

    # 2. Call voice provider
    try:
        provider = get_voice_provider()
        result = await provider.create_web_call(
            metadata=metadata,
            dynamic_variables=dynamic_variables
        )
    except VoiceProviderError as e:
        logger.error("Failed to create web call through provider: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": {"code": "PROVIDER_ERROR", "message": "Failed to establish voice session with provider"}}
        )
    except Exception as e:
        logger.error("Unexpected error creating web call: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Failed to create web call session"}}
        )

    # 3. Pre-create internal call record to associate the browser call
    try:
        call_repo = CallRepository()
        existing = call_repo.get_by_provider_call_id(result.provider_call_id)
        if not existing:
            new_call = CallModel(
                providerCallId=result.provider_call_id,
                direction="inbound",
                fromNumber="Customer",
                toNumber="Le Gourmet Assistant",
                language="fr/en",
                intent="UNKNOWN",
                status="REGISTERED"
            )
            call_repo.create(new_call)
    except Exception as e:
        # Non-fatal: if DB fails, webhook will still upsert when call starts
        logger.warning("Could not pre-persist web call record: %s", str(e))

    logger.info("Web call session created successfully", extra={"call_id": result.provider_call_id})

    # Return only browser-safe data
    return WebCallResponse(
        provider=result.provider,
        call_id=result.provider_call_id,
        access_token=result.access_token,
        status=result.status
    )

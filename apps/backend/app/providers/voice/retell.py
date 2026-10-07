import logging
from typing import Any, Dict, Optional

from app.config.settings import settings
from app.integrations.retell.client import RetellClient
from app.integrations.retell.exceptions import RetellError
from app.integrations.retell.models import RetellCreateCallRequest
from app.providers.voice.base import VoiceCallResult, VoiceProvider, VoiceProviderError

logger = logging.getLogger(__name__)

class RetellVoiceProvider(VoiceProvider):
    def __init__(self) -> None:
        self.client = RetellClient()
        self.agent_id = settings.retell_agent_id
        self.phone_number = settings.retell_phone_number
        
        if not self.agent_id:
            raise VoiceProviderError("RETELL_AGENT_ID is not configured")
        if not self.phone_number:
            raise VoiceProviderError("RETELL_PHONE_NUMBER is not configured")

    async def create_outbound_call(self, to_number: str, metadata: Optional[Dict[str, Any]] = None) -> VoiceCallResult:
        try:
            request = RetellCreateCallRequest(
                from_number=self.phone_number,
                to_number=to_number,
                override_agent_id=self.agent_id,
                retell_llm_dynamic_variables=metadata
            )
            response = await self.client.create_phone_call(request)
            return VoiceCallResult(
                provider="retell",
                provider_call_id=response.call_id,
                status=response.call_status
            )
        except RetellError as e:
            logger.error("Provider failed to create outbound call", exc_info=True)
            raise VoiceProviderError(f"Retell provider error: {str(e)}") from e

    async def get_call(self, provider_call_id: str) -> VoiceCallResult:
        try:
            response = await self.client.get_call(provider_call_id)
            return VoiceCallResult(
                provider="retell",
                provider_call_id=response.call_id,
                status=response.call_status
            )
        except RetellError as e:
            logger.error("Provider failed to get call", exc_info=True)
            raise VoiceProviderError(f"Retell provider error: {str(e)}") from e

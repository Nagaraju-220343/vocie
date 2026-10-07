from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class VoiceProviderError(Exception):
    """Base exception for all Voice Provider errors."""
    pass

class VoiceCallResult(BaseModel):
    provider: str
    provider_call_id: str
    status: str

class VoiceProvider(ABC):
    @abstractmethod
    async def create_outbound_call(self, to_number: str, metadata: Optional[Dict[str, Any]] = None) -> VoiceCallResult:
        """
        Initiates an outbound voice call to the given phone number.
        """
        pass

    @abstractmethod
    async def get_call(self, provider_call_id: str) -> VoiceCallResult:
        """
        Retrieves the status of an existing call from the provider.
        """
        pass

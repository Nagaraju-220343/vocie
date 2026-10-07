import logging
from typing import Dict

import httpx

from app.config.settings import settings
from app.integrations.retell.exceptions import (
    RetellAPIError,
    RetellAuthenticationError,
    RetellConfigurationError,
    RetellNetworkError,
)
from app.integrations.retell.models import RetellCallResponse, RetellCreateCallRequest

logger = logging.getLogger(__name__)

class RetellClient:
    def __init__(self) -> None:
        self.api_key = settings.retell_api_key
        if not self.api_key:
            raise RetellConfigurationError("RETELL_API_KEY is not configured")
        
        self.base_url = "https://api.retellai.com"
        self.timeout = settings.retell_api_timeout_seconds

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_phone_call(self, request: RetellCreateCallRequest) -> RetellCallResponse:
        url = f"{self.base_url}/v2/create-phone-call"
        logger.info("retell.call.create.started", extra={"to_number": request.to_number})
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url, 
                    headers=self._get_headers(), 
                    json=request.model_dump(exclude_none=True)
                )
                
            self._handle_response_errors(response)
            
            data = response.json()
            logger.info("retell.call.create.success", extra={"call_id": data.get("call_id")})
            return RetellCallResponse(**data)
            
        except httpx.RequestError as e:
            logger.error("retell.call.create.failed", extra={"error": str(e)})
            raise RetellNetworkError(f"Network error calling Retell: {str(e)}")

    async def get_call(self, call_id: str) -> RetellCallResponse:
        url = f"{self.base_url}/v2/get-call/{call_id}"
        logger.info("retell.call.get.started", extra={"call_id": call_id})
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url, 
                    headers=self._get_headers()
                )
                
            self._handle_response_errors(response)
            
            data = response.json()
            logger.info("retell.call.get.success", extra={"call_id": call_id})
            return RetellCallResponse(**data)
            
        except httpx.RequestError as e:
            logger.error("retell.call.get.failed", extra={"call_id": call_id, "error": str(e)})
            raise RetellNetworkError(f"Network error calling Retell: {str(e)}")

    def _handle_response_errors(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise RetellAuthenticationError("Retell authentication failed")
            
        if not response.is_success:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"text": response.text}
            raise RetellAPIError(
                message=f"Retell API error: {response.status_code}",
                status_code=response.status_code,
                response_data=error_data
            )

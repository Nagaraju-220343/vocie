from typing import Any, Generator
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.config.settings import settings
from app.integrations.retell.client import RetellClient
from app.integrations.retell.exceptions import (
    RetellAPIError,
    RetellAuthenticationError,
    RetellConfigurationError,
    RetellNetworkError,
)
from app.integrations.retell.models import RetellCreateCallRequest
from app.providers.voice.base import VoiceProviderError
from app.providers.voice.retell import RetellVoiceProvider


@pytest.fixture
def mock_settings() -> Generator[Any, None, None]:
    settings.retell_api_key = "test_api_key"
    settings.retell_agent_id = "test_agent_id"
    settings.retell_phone_number = "+1234567890"
    yield settings
    # Reset
    settings.retell_api_key = ""
    settings.retell_agent_id = ""
    settings.retell_phone_number = ""

@pytest.fixture
def retell_client(mock_settings: Any) -> RetellClient:
    return RetellClient()

@pytest.fixture
def voice_provider(mock_settings: Any) -> RetellVoiceProvider:
    return RetellVoiceProvider()

@pytest.mark.anyio
async def test_client_create_call_success(retell_client: RetellClient) -> None:
    mock_response = httpx.Response(
        200, 
        json={
            "call_id": "call_123",
            "call_status": "registered",
            "agent_id": "test_agent_id",
            "from_number": "+1234567890",
            "to_number": "+0987654321"
        },
        request=httpx.Request("POST", "https://api.retellai.com")
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        req = RetellCreateCallRequest(from_number="+1234567890", to_number="+0987654321")
        res = await retell_client.create_phone_call(req)
        
        assert res.call_id == "call_123"
        assert res.call_status == "registered"

@pytest.mark.anyio
async def test_client_auth_error(retell_client: RetellClient) -> None:
    mock_response = httpx.Response(
        401, 
        json={"error": "Unauthorized"},
        request=httpx.Request("POST", "https://api.retellai.com")
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        with pytest.raises(RetellAuthenticationError):
            req = RetellCreateCallRequest(from_number="+1234567890", to_number="+0987654321")
            await retell_client.create_phone_call(req)

@pytest.mark.anyio
async def test_client_api_error(retell_client: RetellClient) -> None:
    mock_response = httpx.Response(
        400, 
        json={"error": "Bad Request"},
        request=httpx.Request("POST", "https://api.retellai.com")
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        with pytest.raises(RetellAPIError):
            req = RetellCreateCallRequest(from_number="+1234567890", to_number="+0987654321")
            await retell_client.create_phone_call(req)

@pytest.mark.anyio
async def test_client_network_error(retell_client: RetellClient) -> None:
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Timeout")
        
        with pytest.raises(RetellNetworkError):
            req = RetellCreateCallRequest(from_number="+1234567890", to_number="+0987654321")
            await retell_client.create_phone_call(req)

@pytest.mark.anyio
async def test_provider_create_outbound_call(voice_provider: RetellVoiceProvider) -> None:
    mock_response = httpx.Response(
        200, 
        json={
            "call_id": "call_abc",
            "call_status": "registered",
            "agent_id": "test_agent_id",
            "from_number": "+1234567890",
            "to_number": "+1111111111"
        },
        request=httpx.Request("POST", "https://api.retellai.com")
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        res = await voice_provider.create_outbound_call("+1111111111")
        assert res.provider == "retell"
        assert res.provider_call_id == "call_abc"
        assert res.status == "registered"

@pytest.mark.anyio
async def test_provider_get_call(voice_provider: RetellVoiceProvider) -> None:
    mock_response = httpx.Response(
        200, 
        json={
            "call_id": "call_abc",
            "call_status": "ongoing",
            "agent_id": "test_agent_id",
            "from_number": "+1234567890",
            "to_number": "+1111111111"
        },
        request=httpx.Request("GET", "https://api.retellai.com")
    )
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        
        res = await voice_provider.get_call("call_abc")
        assert res.provider == "retell"
        assert res.provider_call_id == "call_abc"
        assert res.status == "ongoing"

def test_missing_config() -> None:
    # Test that missing API key raises error
    settings.retell_api_key = ""
    with pytest.raises(RetellConfigurationError):
        RetellClient()
    
    settings.retell_api_key = "key"
    settings.retell_agent_id = ""
    with pytest.raises(VoiceProviderError):
        RetellVoiceProvider()

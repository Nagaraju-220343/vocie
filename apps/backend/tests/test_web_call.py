from typing import Any, Generator
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import httpx
import pytest

from app.config.settings import settings
from app.repositories.call_repository import CallRepository


@pytest.fixture
def mock_retell_env() -> Generator[Any, None, None]:
    original_key = settings.retell_api_key
    original_agent = settings.retell_agent_id
    settings.retell_api_key = "test_key_12345"
    settings.retell_agent_id = "agent_test_abc"
    yield settings
    settings.retell_api_key = original_key
    settings.retell_agent_id = original_agent


def test_web_call_success_mocked(client: TestClient, mock_retell_env: Any) -> None:
    """1. Successful web-call creation with a mocked Retell API response."""
    mock_retell_payload = {
        "call_id": "call_mocked_web_123",
        "access_token": "token_xyz_temporary_token",
        "call_status": "registered",
        "agent_id": "agent_test_abc",
        "call_type": "web_call"
    }
    mock_response = httpx.Response(
        201,
        json=mock_retell_payload,
        request=httpx.Request("POST", "https://api.retellai.com/v2/create-web-call")
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        res = client.post("/api/voice/web-call", json={})
        assert res.status_code == 201
        data = res.json()
        assert data["provider"] == "retell"
        assert data["call_id"] == "call_mocked_web_123"
        assert data["access_token"] == "token_xyz_temporary_token"
        assert data["status"] == "registered"

        # 6. Verify that API key/secrets are never returned
        assert "key_12345" not in res.text
        assert "Authorization" not in res.text

        # 7. Check correct association between provider call ID and internal call record
        call_repo = CallRepository()
        call = call_repo.get_by_provider_call_id("call_mocked_web_123")
        assert call is not None
        assert call.providerCallId == "call_mocked_web_123"
        assert call.status == "REGISTERED"
        assert call.fromNumber in ["Customer", "Web Browser"]


def test_web_call_missing_api_key(client: TestClient, mock_retell_env: Any) -> None:
    """2. Missing API key."""
    settings.retell_api_key = ""
    res = client.post("/api/voice/web-call", json={})
    assert res.status_code == 500
    data = res.json()
    assert data["detail"]["error"]["code"] == "CONFIGURATION_ERROR"
    assert "key" not in res.text.lower() or "credentials" in res.text.lower()


def test_web_call_missing_agent_id(client: TestClient, mock_retell_env: Any) -> None:
    """3. Missing agent ID."""
    settings.retell_agent_id = ""
    res = client.post("/api/voice/web-call", json={})
    assert res.status_code == 500
    data = res.json()
    assert data["detail"]["error"]["code"] == "CONFIGURATION_ERROR"


def test_web_call_retell_api_failure(client: TestClient, mock_retell_env: Any) -> None:
    """4. Retell API failure (e.g. 500 error from provider)."""
    mock_response = httpx.Response(
        500,
        text="Internal Server Error from Retell",
        request=httpx.Request("POST", "https://api.retellai.com/v2/create-web-call")
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        res = client.post("/api/voice/web-call", json={})
        assert res.status_code == 502
        data = res.json()
        assert data["detail"]["error"]["code"] == "PROVIDER_ERROR"
        # Secrets should not be exposed
        assert "test_key_12345" not in res.text


def test_web_call_malformed_provider_response(client: TestClient, mock_retell_env: Any) -> None:
    """5. Malformed or unexpected provider response."""
    mock_response = httpx.Response(
        201,
        json={"unexpected_field": "no_call_id"},
        request=httpx.Request("POST", "https://api.retellai.com/v2/create-web-call")
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        res = client.post("/api/voice/web-call", json={})
        assert res.status_code in [500, 502]
        # Should not expose internal details or crash the server unhandled
        data = res.json()
        assert "error" in data["detail"]


def test_web_call_does_not_duplicate_when_webhook_arrives(client: TestClient, mock_retell_env: Any) -> None:
    """Verify pre-created call record merges seamlessly when call_started webhook arrives."""
    call_id = "call_mock_dedup_001"
    mock_retell_payload = {
        "call_id": call_id,
        "access_token": "token_test_abc",
        "call_status": "registered",
        "agent_id": "agent_test_abc",
    }
    mock_response = httpx.Response(
        201,
        json=mock_retell_payload,
        request=httpx.Request("POST", "https://api.retellai.com/v2/create-web-call")
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = client.post("/api/voice/web-call", json={})
        assert res.status_code == 201

    call_repo = CallRepository()
    initial_call = call_repo.get_by_provider_call_id(call_id)
    assert initial_call is not None

    # Now simulate webhook call_started for the same call
    from tests.e2e.test_webhook_flow import create_signature
    import json
    payload_start = {
        "event": "call_started",
        "call": {
            "call_id": call_id,
        }
    }
    payload_bytes = json.dumps(payload_start).encode("utf-8")
    headers = {"X-Retell-Signature": create_signature(payload_bytes), "Content-Type": "application/json"}
    webhook_res = client.post("/api/webhooks/retell", content=payload_bytes, headers=headers)
    assert webhook_res.status_code == 200

    # Ensure only ONE record exists and its status transitioned to IN_PROGRESS
    matching_calls = [c for c in call_repo.list() if c.providerCallId == call_id]
    assert len(matching_calls) == 1
    assert matching_calls[0].status == "IN_PROGRESS"

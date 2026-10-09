import hmac
import hashlib
import json
import time
import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.repositories.call_repository import CallRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository

def create_signature(payload_bytes: bytes) -> str:
    secret = settings.retell_api_key
    timestamp = int(time.time() * 1000)
    input_str = payload_bytes.decode("utf-8") + str(timestamp)
    digest = hmac.new(secret.encode("utf-8"), input_str.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"v={timestamp},d={digest}"

@pytest.fixture
def call_repo():
    return CallRepository()

@pytest.fixture
def customer_repo():
    return CustomerRepository()

@pytest.fixture
def order_repo():
    return OrderRepository()

def test_full_webhook_order_flow(client: TestClient, call_repo, customer_repo, order_repo):
    settings.retell_api_key = "test_api_key"
    # Simulate call started
    payload_start = {
        "event": "call_started",
        "call": {
            "call_id": "test_call_fr_001",
        }
    }
    
    payload_bytes = json.dumps(payload_start).encode("utf-8")
    headers = {"X-Retell-Signature": create_signature(payload_bytes), "Content-Type": "application/json"}
    res = client.post("/api/webhooks/retell", content=payload_bytes, headers=headers)
    assert res.status_code == 200
    
    # Check call created
    call = call_repo.get_by_provider_call_id("test_call_fr_001")
    assert call is not None
    assert call.status == "IN_PROGRESS"
    
    # Simulate call ended with full French order transcript
    payload_end = {
        "event": "call_ended",
        "call": {
            "call_id": "test_call_fr_001",
            "transcript": [
                {"role": "user", "content": "Bonjour, je voudrais commander deux pizzas margherita et une salade."},
                {"role": "agent", "content": "Bien sûr. A livrer ou à emporter ? "},
                {"role": "user", "content": "À livrer au 12 Rue de Paris, 75001."},
                {"role": "agent", "content": "Puis-je avoir votre nom et numéro ?"},
                {"role": "user", "content": "Pierre Dupont. 06 12 34 56 78."}
            ]
        }
    }
    
    payload_bytes = json.dumps(payload_end).encode("utf-8")
    headers = {"X-Retell-Signature": create_signature(payload_bytes), "Content-Type": "application/json"}
    res = client.post("/api/webhooks/retell", content=payload_bytes, headers=headers)
    assert res.status_code == 200
    
    call = call_repo.get_by_provider_call_id("test_call_fr_001")
    assert call.status == "COMPLETED"
    assert call.intent == "ORDER"
    assert call.language == "fr"
    
    # Verify customer created
    customers = customer_repo.list()
    assert len(customers) == 1
    assert customers[0].phone == "+33612345678"
    assert customers[0].name == "Pierre Dupont"
    
    # Verify order created
    orders = order_repo.list()
    assert len(orders) == 1
    assert orders[0].callId == call.id
    assert orders[0].orderType == "DELIVERY"
    assert orders[0].address == "12 Rue de Paris, 75001"
    assert len(orders[0].items) == 2
    
def test_duplicate_webhook_does_not_duplicate_order(client: TestClient, call_repo, customer_repo, order_repo):
    settings.retell_api_key = "test_api_key"
    payload_end = {
        "event": "call_ended",
        "call": {
            "call_id": "test_call_duplicate",
            "transcript": [
                {"role": "user", "content": "I want to place an order. Two pizzas. Delivery to 12 Rue de Paris. Name is Pierre Dupont. Phone 06 12 34 56 78."}
            ]
        }
    }
    payload_bytes = json.dumps(payload_end).encode("utf-8")
    headers = {"X-Retell-Signature": create_signature(payload_bytes), "Content-Type": "application/json"}
    
    # First time
    res = client.post("/api/webhooks/retell", content=payload_bytes, headers=headers)
    assert res.status_code == 200
    
    # Second time
    res = client.post("/api/webhooks/retell", content=payload_bytes, headers=headers)
    assert res.status_code == 200
    
    # Third time
    res = client.post("/api/webhooks/retell", content=payload_bytes, headers=headers)
    assert res.status_code == 200
    
    call_id = call_repo.get_by_provider_call_id("test_call_duplicate").id
    orders = [o for o in order_repo.list() if o.callId == call_id]
    assert len(orders) == 1 # Only one order should be created

def test_webhook_invalid_signature(client: TestClient):
    settings.retell_api_key = "test_api_key"
    payload = {"event": "call_started"}
    headers = {"X-Retell-Signature": "invalid_signature"}
    res = client.post("/api/webhooks/retell", json=payload, headers=headers)
    assert res.status_code == 401

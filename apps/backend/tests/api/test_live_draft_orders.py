import pytest
from fastapi.testclient import TestClient
from bson.objectid import ObjectId

from app.repositories.order_repository import OrderRepository
from app.repositories.call_repository import CallRepository
from app.models.call import CallModel

@pytest.fixture
def order_repo():
    return OrderRepository()

@pytest.fixture
def call_repo():
    return CallRepository()

def test_live_draft_flow(client: TestClient, order_repo: OrderRepository, call_repo: CallRepository):
    # Setup call
    call_id = "test_live_call_123"
    call = CallModel(providerCallId=call_id, direction="inbound", intent="UNKNOWN", status="IN_PROGRESS", fromNumber="test", toNumber="test", language="test")
    call_doc_id = call_repo.create(call)
    
    # 1. First update_order creates a DRAFT order
    payload1 = {
        "items": [{"name": "Pizza", "quantity": 1}],
        "notes": "Test draft"
    }
    res1 = client.patch(f"/api/orders/{call_id}", json=payload1)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["callId"] == call_id
    assert data1["status"] == "DRAFT"
    assert len(data1["items"]) == 1
    assert data1["items"][0]["name"] == "Pizza"
    assert ObjectId.is_valid(data1["id"])
    mongo_id = data1["id"]
    
    # 2. Second update_order with same call_id updates the same order
    payload2 = {
        "items": [{"name": "Pizza", "quantity": 2}],
        "customerName": "Alice"
    }
    res2 = client.patch(f"/api/orders/{call_id}", json=payload2)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == mongo_id
    assert data2["items"][0]["quantity"] == 2
    assert data2["customerName"] == "Alice"
    
    # 3. No duplicate draft orders are created
    orders = order_repo.find_by_call_id(call_id)
    assert len(orders) == 1
    
    # 6. Missing delivery address fails confirm
    client.patch(f"/api/orders/{call_id}", json={"orderType": "DELIVERY"})
    res3 = client.post(f"/api/orders/{call_id}/confirm")
    assert res3.status_code == 400
    assert "Delivery address is required" in res3.json()["detail"]["error"]["message"]
    
    # 7. Missing customer information fails confirm
    # Fix address, remove customerName (by patching it empty, actually PATCH doesn't remove it easily unless we patch it, but customerName was "Alice" so it's not missing. Let's patch it back)
    # Wait, customerName and phone are required.
    client.patch(f"/api/orders/{call_id}", json={"customerName": "Alice", "phone": "123", "address": "123 Main St", "orderType": "DELIVERY"})
    
    # 4. confirm_order confirms the existing draft
    res4 = client.post(f"/api/orders/{call_id}/confirm")
    assert res4.status_code == 200
    assert res4.json()["status"] == "CONFIRMED"
    
    # 5. confirm_order remains idempotent
    res5 = client.post(f"/api/orders/{call_id}/confirm")
    assert res5.status_code == 200
    assert res5.json()["status"] == "CONFIRMED"

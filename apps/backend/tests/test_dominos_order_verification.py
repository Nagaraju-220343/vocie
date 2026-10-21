import json
import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.repositories.call_repository import CallRepository
from app.repositories.order_repository import OrderRepository
from app.models.call import CallModel
from app.models.order import OrderModel, OrderItemModel
from tests.e2e.test_webhook_flow import create_signature


@pytest.fixture
def call_repo():
    return CallRepository()


@pytest.fixture
def order_repo():
    return OrderRepository()


def test_dominos_draft_persistence_success(client: TestClient, order_repo: OrderRepository):
    """
    1. update_order validates request body, maps call_id to draft order,
       persists to dev database, and returns clear success response.
    """
    call_id = "retell_call_dominos_001"
    payload = {
        "restaurant": "dominos_le_chesnay",
        "orderType": "DELIVERY",
        "customerName": "Antoine Martin",
        "phone": "+33611223344",
        "address": "48 Rue de Versailles, 78150 Le Chesnay",
        "items": [
            {
                "name": "Pizza Cannibale",
                "quantity": 2,
                "price": 14.99,
                "size": "Medium",
                "crust": "Classique",
                "options": ["extra_cheese"]
            },
            {
                "name": "Coca-Cola 1.5L",
                "quantity": 1,
                "price": 3.50
            }
        ],
        "notes": "Code porte: 1234"
    }

    response = client.patch(f"/api/orders/{call_id}", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify response contract
    assert data["success"] is True
    assert data["order_id"] is not None
    assert data["callId"] == call_id
    assert data["status"] in ["draft_saved", "DRAFT"]
    assert data["message"] == "Order draft saved successfully"
    assert data["restaurant"] == "dominos_le_chesnay"
    assert len(data["items"]) == 2

    # Verify persisted in database
    persisted_orders = order_repo.find_by_call_id(call_id)
    assert len(persisted_orders) == 1
    assert persisted_orders[0].customerName == "Antoine Martin"
    assert persisted_orders[0].items[0].name == "Pizza Cannibale"
    assert persisted_orders[0].items[0].quantity == 2


def test_dominos_draft_persistence_failure_validation(client: TestClient):
    """
    2. update_order returns meaningful non-success response if validation fails
       (e.g., negative quantity or empty item name).
    """
    call_id = "retell_call_dominos_002"

    # Negative quantity
    payload_invalid_qty = {
        "items": [{"name": "Pizza 4 Fromages", "quantity": -1}]
    }
    res_qty = client.patch(f"/api/orders/{call_id}", json=payload_invalid_qty)
    assert res_qty.status_code == 400
    assert "Invalid quantity" in res_qty.json()["detail"]["error"]["message"]

    # Empty item name
    payload_empty_name = {
        "items": [{"name": "", "quantity": 1}]
    }
    res_name = client.patch(f"/api/orders/{call_id}", json=payload_empty_name)
    assert res_name.status_code == 400
    assert "Item name cannot be empty" in res_name.json()["detail"]["error"]["message"]

    # Empty items list
    payload_empty_items = {
        "items": []
    }
    res_empty = client.patch(f"/api/orders/{call_id}", json=payload_empty_items)
    assert res_empty.status_code == 400
    assert "Order items cannot be empty" in res_empty.json()["detail"]["error"]["message"]


def test_dominos_confirm_when_draft_does_not_exist(client: TestClient):
    """
    3. confirm_order rejects confirmation if the draft does not exist.
    """
    non_existent_call_id = "call_never_created_999"
    response = client.post(f"/api/orders/{non_existent_call_id}/confirm")
    assert response.status_code == 404
    detail = response.json()["detail"]["error"]
    assert "does not exist" in detail["message"] or "not found" in detail["message"].lower()


def test_dominos_confirm_order_success(client: TestClient, order_repo: OrderRepository):
    """
    4. confirm_order retrieves saved draft, verifies required details,
       persists CONFIRMED status, and returns confirmed order ID and status.
    """
    call_id = "retell_call_dominos_004"
    draft_payload = {
        "restaurant": "dominos_le_chesnay",
        "orderType": "DELIVERY",
        "customerName": "Claire Dupont",
        "phone": "+33698765432",
        "address": "10 Route de Saint-Germain, 78150 Le Chesnay",
        "items": [
            {"name": "Pizza Reine", "quantity": 1, "price": 12.50}
        ]
    }
    # 1. Create draft
    draft_res = client.patch(f"/api/orders/{call_id}", json=draft_payload)
    assert draft_res.status_code == 200
    order_id = draft_res.json()["order_id"]

    # 2. Confirm order
    confirm_res = client.post(f"/api/orders/{call_id}/confirm")
    assert confirm_res.status_code == 200
    data = confirm_res.json()

    assert data["success"] is True
    assert data["order_id"] == order_id
    assert data["status"] in ["confirmed", "CONFIRMED"]
    assert data["message"] == "Order confirmed successfully"

    # Verify persisted in database
    db_order = order_repo.get_by_id(order_id)
    assert db_order is not None
    assert db_order.status == "CONFIRMED"


def test_dominos_confirm_order_failure_missing_address_for_delivery(client: TestClient):
    """
    5. confirm_order rejects confirmation when delivery address is missing for DELIVERY orders.
    """
    call_id = "retell_call_dominos_005"
    draft_payload = {
        "orderType": "DELIVERY",
        "customerName": "Marc Vasseur",
        "phone": "+33612345678",
        "items": [
            {"name": "Pizza Peppina", "quantity": 1}
        ]
        # Notice: address is deliberately omitted
    }
    client.patch(f"/api/orders/{call_id}", json=draft_payload)

    confirm_res = client.post(f"/api/orders/{call_id}/confirm")
    assert confirm_res.status_code == 400
    assert "Delivery address is required" in confirm_res.json()["detail"]["error"]["message"]


def test_dominos_confirm_order_failure_no_valid_items(client: TestClient, order_repo: OrderRepository):
    """
    6. confirm_order rejects confirmation if draft has no valid items.
    """
    call_id = "retell_call_dominos_006"
    # Create empty draft order directly
    empty_order = OrderModel(
        callId=call_id,
        customerName="Jean Test",
        phone="+33600000000",
        orderType="PICKUP",
        items=[],
        status="DRAFT"
    )
    order_id = order_repo.create(empty_order)

    confirm_res = client.post(f"/api/orders/{order_id}/confirm")
    assert confirm_res.status_code == 400
    assert "at least one valid item" in confirm_res.json()["detail"]["error"]["message"]


def test_dominos_duplicate_confirmation_prevention(client: TestClient, order_repo: OrderRepository):
    """
    7. confirm_order prevents accidental duplicate confirmations while remaining idempotent.
    """
    call_id = "retell_call_dominos_007"
    draft_payload = {
        "orderType": "PICKUP",
        "customerName": "Sophie Laurent",
        "phone": "+33655443322",
        "items": [{"name": "Pizza Chèvre-Miel", "quantity": 1}]
    }
    client.patch(f"/api/orders/{call_id}", json=draft_payload)

    # First confirmation
    res1 = client.post(f"/api/orders/{call_id}/confirm")
    assert res1.status_code == 200
    assert res1.json()["status"] in ["confirmed", "CONFIRMED"]
    first_order_id = res1.json()["order_id"]

    # Second confirmation attempt
    res2 = client.post(f"/api/orders/{call_id}/confirm")
    assert res2.status_code == 200
    assert res2.json()["status"] in ["confirmed", "CONFIRMED"]
    assert res2.json()["order_id"] == first_order_id

    # Verify no duplicate orders created in DB
    orders = order_repo.find_by_call_id(call_id)
    assert len(orders) == 1


def test_call_ended_webhook_does_not_overwrite_dominos_order(client: TestClient, call_repo: CallRepository, order_repo: OrderRepository):
    """
    8. Retell call_ended webhook must NOT overwrite Domino's order items
       with legacy Dominos Le Chesnay regex dishes, while preserving webhook signature verification.
    """
    settings.retell_api_key = "test_api_key"
    call_id = "retell_dominos_webhook_call_008"

    # Step 1: Pre-populate Domino's draft order created during call via update_order
    draft_payload = {
        "restaurant": "dominos_le_chesnay",
        "orderType": "DELIVERY",
        "customerName": "Julien Clerc",
        "phone": "+33677889900",
        "address": "12 Rue de Versailles, 78150 Le Chesnay",
        "items": [
            {
                "name": "Pizza Boursin",
                "quantity": 2,
                "price": 13.99,
                "size": "Large"
            }
        ]
    }
    draft_res = client.patch(f"/api/orders/{call_id}", json=draft_payload)
    assert draft_res.status_code == 200

    # Confirm the order
    conf_res = client.post(f"/api/orders/{call_id}/confirm")
    assert conf_res.status_code == 200
    assert conf_res.json()["status"] in ["confirmed", "CONFIRMED"]

    # Step 2: Trigger call_ended webhook with French words that would otherwise
    # trigger legacy Dominos Le Chesnay regexes (e.g., 'burger', 'salade')
    webhook_payload = {
        "event": "call_ended",
        "call": {
            "call_id": call_id,
            "transcript": [
                {"role": "user", "content": "Je voudrais aussi un burger et une salade mais finalement non."},
                {"role": "agent", "content": "Votre commande de pizza Boursin est bien confirmée."}
            ]
        }
    }
    payload_bytes = json.dumps(webhook_payload).encode("utf-8")
    signature = create_signature(payload_bytes)

    # Check invalid signature rejection works
    bad_headers = {"X-Retell-Signature": "invalid_sig", "Content-Type": "application/json"}
    bad_res = client.post("/api/webhooks/retell", content=payload_bytes, headers=bad_headers)
    assert bad_res.status_code == 401

    # Send valid signature
    valid_headers = {"X-Retell-Signature": signature, "Content-Type": "application/json"}
    good_res = client.post("/api/webhooks/retell", content=payload_bytes, headers=valid_headers)
    assert good_res.status_code == 200

    # Step 3: Verify Domino's order was preserved and not overwritten with Dominos Le Chesnay burger/salade
    orders = order_repo.find_by_call_id(call_id)
    assert len(orders) == 1
    dominos_order = orders[0]
    assert dominos_order.status == "CONFIRMED"
    assert len(dominos_order.items) == 1
    assert dominos_order.items[0].name == "Pizza Boursin"
    assert dominos_order.items[0].quantity == 2
    assert dominos_order.customerName == "Julien Clerc"

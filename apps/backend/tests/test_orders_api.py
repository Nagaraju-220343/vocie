
def test_create_order(client):
    payload = {
        "callId": "call_abc",
        "customerName": "Test Customer",
        "orderType": "DELIVERY",
        "items": [{"name": "Burger", "quantity": 2, "price": 10.0}]
    }
    response = client.post("/api/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["callId"] == "call_abc"
    assert len(data["items"]) == 1

def test_create_order_invalid(client):
    payload = {
        "callId": "call_abc",
        "items": "not a list"
    }
    res = client.post("/api/orders", json=payload)
    assert res.status_code == 422

def test_get_orders(client):
    payload = {
        "callId": "call_123",
        "items": [{"name": "Fries", "quantity": 1}]
    }
    res = client.post("/api/orders", json=payload)
    order_id = res.json()["id"]

    res_single = client.get(f"/api/orders/{order_id}")
    assert res_single.status_code == 200

    res_list = client.get("/api/orders")
    assert res_list.status_code == 200
    assert len(res_list.json()["data"]) > 0

def test_update_order(client):
    payload = {
        "callId": "call_update",
        "items": [{"name": "Soda", "quantity": 1}]
    }
    res = client.post("/api/orders", json=payload)
    order_id = res.json()["id"]

    patch_res = client.patch(f"/api/orders/{order_id}", json={"status": "COMPLETED"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "COMPLETED"

def test_confirm_order_success(client):
    payload = {
        "callId": "call_conf",
        "customerName": "Test Customer",
        "phone": "123",
        "orderType": "PICKUP",
        "items": [{"name": "Soda", "quantity": 1}]
    }
    res = client.post("/api/orders", json=payload)
    order_id = res.json()["id"]

    conf_res = client.post(f"/api/orders/{order_id}/confirm")
    assert conf_res.status_code == 200
    assert conf_res.json()["status"] == "CONFIRMED"
    
def test_confirm_order_missing_customer(client):
    payload = {
        "callId": "call_conf_2",
        "orderType": "PICKUP",
        "items": [{"name": "Soda", "quantity": 1}]
    }
    res = client.post("/api/orders", json=payload)
    order_id = res.json()["id"]

    conf_res = client.post(f"/api/orders/{order_id}/confirm")
    assert conf_res.status_code == 400
    assert "Customer name or phone is required" in conf_res.json()["detail"]["error"]["message"]

def test_confirm_order_missing_address_delivery(client):
    payload = {
        "callId": "call_conf_3",
        "customerName": "Test Customer",
        "orderType": "DELIVERY",
        "items": [{"name": "Soda", "quantity": 1}]
    }
    res = client.post("/api/orders", json=payload)
    order_id = res.json()["id"]

    conf_res = client.post(f"/api/orders/{order_id}/confirm")
    assert conf_res.status_code == 400
    assert "Delivery address is required" in conf_res.json()["detail"]["error"]["message"]

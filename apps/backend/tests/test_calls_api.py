
def test_create_call(client):
    payload = {
        "providerCallId": "call_123",
        "direction": "inbound",
        "fromNumber": "+1234567890",
        "toNumber": "+0987654321",
        "language": "EN",
        "intent": "order",
        "status": "in-progress"
    }
    response = client.post("/api/calls", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["providerCallId"] == "call_123"
    assert "id" in data

def test_create_call_duplicate(client):
    payload = {
        "providerCallId": "call_dup",
        "direction": "inbound",
        "fromNumber": "+1234567890",
        "toNumber": "+0987654321",
        "language": "EN",
        "intent": "order",
        "status": "in-progress"
    }
    r1 = client.post("/api/calls", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/calls", json=payload)
    assert r2.status_code == 409

def test_get_call_not_found(client):
    response = client.get("/api/calls/65e90d79f0f9b31d4e0a7abc")
    assert response.status_code == 404

def test_get_calls_and_single(client):
    payload = {
        "providerCallId": "call_456",
        "direction": "inbound",
        "fromNumber": "+1234567890",
        "toNumber": "+0987654321",
        "language": "EN",
        "intent": "order",
        "status": "in-progress"
    }
    res = client.post("/api/calls", json=payload)
    call_id = res.json()["id"]

    res_single = client.get(f"/api/calls/{call_id}")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == call_id

    res_list = client.get("/api/calls")
    assert res_list.status_code == 200
    assert len(res_list.json()["data"]) > 0

def test_update_call(client):
    payload = {
        "providerCallId": "call_789",
        "direction": "inbound",
        "fromNumber": "+1234567890",
        "toNumber": "+0987654321",
        "language": "EN",
        "intent": "order",
        "status": "in-progress"
    }
    res = client.post("/api/calls", json=payload)
    call_id = res.json()["id"]

    patch_res = client.patch(f"/api/calls/{call_id}", json={"status": "completed"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "completed"

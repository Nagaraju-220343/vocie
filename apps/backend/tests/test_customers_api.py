
def test_create_customer(client):
    payload = {"phone": "+123456", "name": "John"}
    response = client.post("/api/customers", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "John"

def test_get_customers(client):
    res = client.post("/api/customers", json={"phone": "+999"})
    cid = res.json()["id"]

    res_single = client.get(f"/api/customers/{cid}")
    assert res_single.status_code == 200

    res_list = client.get("/api/customers")
    assert res_list.status_code == 200
    assert len(res_list.json()["data"]) > 0

def test_update_customer(client):
    res = client.post("/api/customers", json={"phone": "+888"})
    cid = res.json()["id"]

    patch = client.patch(f"/api/customers/{cid}", json={"name": "Alice"})
    assert patch.status_code == 200
    assert patch.json()["name"] == "Alice"

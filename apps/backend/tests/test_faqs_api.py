import pytest

def test_create_faq(client):
    payload = {
        "question": "What time?",
        "answerFr": "Heure",
        "answerEn": "Time",
        "category": "HOURS",
        "active": True
    }
    response = client.post("/api/faqs", json=payload)
    assert response.status_code == 201
    assert response.json()["question"] == "What time?"

def test_get_faqs(client):
    res = client.post("/api/faqs", json={
        "question": "Q1", "answerFr": "A1F", "answerEn": "A1E", "category": "C"
    })
    fid = res.json()["id"]

    res_single = client.get(f"/api/faqs/{fid}")
    assert res_single.status_code == 200

    res_list = client.get("/api/faqs")
    assert res_list.status_code == 200

def test_update_faq(client):
    res = client.post("/api/faqs", json={
        "question": "Q2", "answerFr": "F", "answerEn": "E", "category": "C"
    })
    fid = res.json()["id"]

    patch = client.patch(f"/api/faqs/{fid}", json={"answerEn": "E_NEW"})
    assert patch.status_code == 200
    assert patch.json()["answerEn"] == "E_NEW"

def test_delete_faq(client):
    res = client.post("/api/faqs", json={
        "question": "Q3", "answerFr": "F", "answerEn": "E", "category": "C"
    })
    fid = res.json()["id"]

    del_res = client.delete(f"/api/faqs/{fid}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/faqs/{fid}")
    assert get_res.status_code == 404

def test_faq_search(client):
    client.post("/api/faqs", json={
        "question": "What is the password?",
        "answerFr": "mot de passe",
        "answerEn": "1234",
        "category": "WIFI",
        "active": True
    })

    # Search existing
    res1 = client.get("/api/faqs/search?q=what is the wifi password&language=EN")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["matched"] is True
    assert data1["answer"] == "1234"

    # Search unknown
    res2 = client.get("/api/faqs/search?q=do you have aliens&language=EN")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["matched"] is False
    assert data2["answer"] is None

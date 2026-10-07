import pytest

def test_create_feedback(client):
    payload = {
        "callId": "call_123",
        "field": "intent",
        "correctedValue": "new_intent"
    }
    res = client.post("/api/feedback", json=payload)
    assert res.status_code == 201
    assert res.json()["field"] == "intent"

def test_get_feedback(client):
    client.post("/api/feedback", json={
        "callId": "call_123", "field": "f1"
    })

    res = client.get("/api/feedback")
    assert res.status_code == 200
    assert len(res.json()["data"]) > 0

def test_get_feedback_by_call(client):
    client.post("/api/feedback", json={
        "callId": "call_999", "field": "f2"
    })
    res = client.get("/api/calls/call_999/feedback")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    assert res.json()[0]["callId"] == "call_999"

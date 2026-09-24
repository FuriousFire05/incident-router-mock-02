from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_route_payment_issue():
    response = client.post("/route", json={"message": "My withdrawal is still pending"})
    assert response.status_code == 200
    body = response.json()
    assert body["team"] == "payments"
    assert body["severity"] == "medium"
    assert 0 <= body["confidence"] <= 1

def test_route_rejects_blank_message():
    response = client.post("/route", json={"message": "   "})
    assert response.status_code == 422

def test_route_rejects_extra_fields():
    response = client.post("/route", json={"message": "The website crashed", "unexpected": True})
    assert response.status_code == 422

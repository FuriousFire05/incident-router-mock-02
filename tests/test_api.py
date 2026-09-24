import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_counters():
    app.state.counters.reset()
    yield
    app.state.counters.reset()

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

def test_route_accepts_metadata_and_applies_vip_escalation():
    response = client.post(
        "/route",
        json={
            "message": "  My withdrawal is delayed  ",
            "customer_tier": "vip",
            "source": "mobile",
        },
    )
    assert response.status_code == 200
    assert response.json()["team"] == "payments"
    assert response.json()["severity"] == "high"

@pytest.mark.parametrize(
    ("field", "value"),
    [("customer_tier", "premium"), ("source", "email")],
)
def test_route_rejects_invalid_metadata(field, value):
    response = client.post("/route", json={"message": "Help", field: value})
    assert response.status_code == 422

def test_batch_preserves_order():
    response = client.post(
        "/route/batch",
        json={
            "items": [
                {"message": "My withdrawal is delayed"},
                {"message": "The mobile app crashed", "source": "mobile"},
                {"message": "A general question"},
            ]
        },
    )
    assert response.status_code == 200
    assert [result["team"] for result in response.json()["results"]] == [
        "payments",
        "platform",
        "general",
    ]

def test_batch_rejects_empty_items():
    response = client.post("/route/batch", json={"items": []})
    assert response.status_code == 422

def test_batch_rejects_more_than_twenty_items():
    response = client.post(
        "/route/batch",
        json={"items": [{"message": f"Incident {index}"} for index in range(21)]},
    )
    assert response.status_code == 422

def test_batch_rejects_unexpected_outer_fields():
    response = client.post(
        "/route/batch",
        json={"items": [{"message": "Help"}], "unexpected": True},
    )
    assert response.status_code == 422

def test_stats_track_single_and_batch_requests():
    single_response = client.post("/route", json={"message": "I was hacked"})
    batch_response = client.post(
        "/route/batch",
        json={
            "items": [
                {"message": "My withdrawal is delayed"},
                {"message": "This may be fraud"},
            ]
        },
    )

    assert single_response.status_code == 200
    assert batch_response.status_code == 200
    assert client.get("/stats").json() == {
        "route_requests": 1,
        "batch_requests": 1,
        "items_routed": 3,
        "critical_results": 2,
    }

def test_invalid_single_request_does_not_alter_stats():
    client.post("/route", json={"message": "My account is blocked"})
    before = client.get("/stats").json()

    response = client.post("/route", json={"message": "   "})

    assert response.status_code == 422
    assert client.get("/stats").json() == before

def test_invalid_batch_request_does_not_alter_stats():
    client.post("/route/batch", json={"items": [{"message": "A question"}]})
    before = client.get("/stats").json()

    response = client.post(
        "/route/batch",
        json={"items": [{"message": "Help", "source": "email"}]},
    )

    assert response.status_code == 422
    assert client.get("/stats").json() == before

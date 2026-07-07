import pytest

@pytest.fixture
def auth_headers(client):
    # Setup helper user and headers
    client.post(
        "/register",
        json={"email": "alerts@example.com", "password": "password123"}
    )
    login_resp = client.post(
        "/login",
        json={"email": "alerts@example.com", "password": "password123"}
    )
    token = login_resp.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}

def test_alert_crud(client, auth_headers):
    # 1. GET /alerts -> should be empty
    resp = client.get("/alerts", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []

    # 2. POST /alerts -> create alert
    payload = {
        "symbol": "TCS",
        "condition": "above",
        "targetPrice": 4500.0
    }
    resp = client.post("/alerts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["symbol"] == "TCS"
    assert data["condition"] == "above"
    assert data["targetPrice"] == 4500.0
    assert "id" in data
    alert_id = data["id"]

    # Test invalid condition type (not above/below)
    invalid_payload = {
        "symbol": "TCS",
        "condition": "greater_than",
        "targetPrice": 4500.0
    }
    resp = client.post("/alerts", json=invalid_payload, headers=auth_headers)
    assert resp.status_code == 422

    # Test duplicate creation
    resp = client.post("/alerts", json=payload, headers=auth_headers)
    assert resp.status_code == 400

    # 3. GET /alerts -> should contain the alert
    resp = client.get("/alerts", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["symbol"] == "TCS"

    # 4. DELETE /alerts/{id} -> delete alert
    resp = client.delete(f"/alerts/{alert_id}", headers=auth_headers)
    assert resp.status_code == 204

    # 5. GET /alerts -> should be empty again
    resp = client.get("/alerts", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []

def test_alert_unauthorized(client):
    # Test that alerts endpoints are secured
    resp = client.get("/alerts")
    assert resp.status_code == 401

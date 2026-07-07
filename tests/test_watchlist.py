import pytest

@pytest.fixture
def auth_headers(client):
    # Setup helper user and headers
    client.post(
        "/register",
        json={"email": "watchlist@example.com", "password": "password123"}
    )
    login_resp = client.post(
        "/login",
        json={"email": "watchlist@example.com", "password": "password123"}
    )
    token = login_resp.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}

def test_watchlist_crud(client, auth_headers):
    # 1. GET /watchlist -> should be empty
    resp = client.get("/watchlist", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []

    # 2. POST /watchlist -> add symbol
    payload = {
        "symbol": "INFY"
    }
    resp = client.post("/watchlist", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["symbol"] == "INFY"
    assert "id" in data
    watchlist_id = data["id"]

    # Test invalid data (empty symbol)
    resp = client.post("/watchlist", json={"symbol": ""}, headers=auth_headers)
    assert resp.status_code == 422

    # Test duplicate creation
    resp = client.post("/watchlist", json=payload, headers=auth_headers)
    assert resp.status_code == 400

    # 3. GET /watchlist -> should contain the symbol
    resp = client.get("/watchlist", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["symbol"] == "INFY"

    # 4. DELETE /watchlist/{id} -> delete
    resp = client.delete(f"/watchlist/{watchlist_id}", headers=auth_headers)
    assert resp.status_code == 204

    # 5. GET /watchlist -> should be empty again
    resp = client.get("/watchlist", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []

def test_watchlist_unauthorized(client):
    # Test that watchlist endpoints are secured
    resp = client.get("/watchlist")
    assert resp.status_code == 401

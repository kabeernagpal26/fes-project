import pytest

@pytest.fixture
def auth_headers(client):
    # Setup helper user and headers
    client.post(
        "/register",
        json={"email": "portfolio@example.com", "password": "password123"}
    )
    login_resp = client.post(
        "/login",
        json={"email": "portfolio@example.com", "password": "password123"}
    )
    token = login_resp.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}

def test_portfolio_crud(client, auth_headers):
    # 1. GET /portfolio -> should be empty
    resp = client.get("/portfolio", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []

    # 2. POST /portfolio -> create item
    payload = {
        "stockSymbol": "RELIANCE",
        "quantity": 20,
        "averagePrice": 1450.5
    }
    resp = client.post("/portfolio", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["stockSymbol"] == "RELIANCE"
    assert data["quantity"] == 20
    assert data["averagePrice"] == 1450.5
    assert "id" in data
    item_id = data["id"]

    # Test invalid data (negative quantity)
    invalid_payload = {
        "stockSymbol": "INFY",
        "quantity": -5,
        "averagePrice": 1000
    }
    resp = client.post("/portfolio", json=invalid_payload, headers=auth_headers)
    assert resp.status_code == 422

    # Test duplicate creation
    resp = client.post("/portfolio", json=payload, headers=auth_headers)
    assert resp.status_code == 400

    # 3. GET /portfolio -> should now contain the item
    resp = client.get("/portfolio", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["stockSymbol"] == "RELIANCE"

    # 4. PUT /portfolio/{id} -> update item
    update_payload = {
        "quantity": 25,
        "averagePrice": 1460.0
    }
    resp = client.put(f"/portfolio/{item_id}", json=update_payload, headers=auth_headers)
    assert resp.status_code == 200
    updated_data = resp.json()
    assert updated_data["quantity"] == 25
    assert updated_data["averagePrice"] == 1460.0

    # 5. DELETE /portfolio/{id} -> delete item
    resp = client.delete(f"/portfolio/{item_id}", headers=auth_headers)
    assert resp.status_code == 204

    # 6. GET /portfolio -> should be empty again
    resp = client.get("/portfolio", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []

def test_portfolio_unauthorized(client):
    # Test that portfolio endpoints are secured
    resp = client.get("/portfolio")
    assert resp.status_code == 401

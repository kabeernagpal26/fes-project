def test_register_user(client):
    # Test successful registration
    response = client.post(
        "/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data  # Ensure password is not returned

    # Test duplicate registration
    response = client.post(
        "/register",
        json={"email": "test@example.com", "password": "password456"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

    # Test validation error (short password)
    response = client.post(
        "/register",
        json={"email": "invalid@example.com", "password": "123"}
    )
    assert response.status_code == 422
    assert "errors" in response.json()

def test_login_user(client):
    # Register user
    client.post(
        "/register",
        json={"email": "user@example.com", "password": "password123"}
    )

    # Test successful login
    response = client.post(
        "/login",
        json={"email": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["tokenType"] == "bearer"

    # Test login with invalid password
    response = client.post(
        "/login",
        json={"email": "user@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_token_refresh(client):
    # Register and login user
    client.post(
        "/register",
        json={"email": "refresh@example.com", "password": "password123"}
    )
    login_resp = client.post(
        "/login",
        json={"email": "refresh@example.com", "password": "password123"}
    )
    refresh_token = login_resp.json()["refreshToken"]

    # Test successful token refresh
    response = client.post(
        "/refresh",
        json={"refreshToken": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert "refreshToken" in data

    # Test refresh with invalid token
    response = client.post(
        "/refresh",
        json={"refreshToken": "invalid-token"}
    )
    assert response.status_code == 401

def test_logout(client):
    # Register and login user
    client.post(
        "/register",
        json={"email": "logout@example.com", "password": "password123"}
    )
    login_resp = client.post(
        "/login",
        json={"email": "logout@example.com", "password": "password123"}
    )
    access_token = login_resp.json()["accessToken"]

    # Test logout
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully logged out"

    # Test requesting protected endpoint after logout (should fail)
    response = client.get("/portfolio", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has been logged out/revoked"

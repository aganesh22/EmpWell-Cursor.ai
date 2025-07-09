import pytest
from fastapi.testclient import TestClient


def test_register_and_login(client: TestClient):
    """Test user registration and login flow."""
    email = "testuser@example.com"
    password = "secret123"
    
    # Register user
    resp = client.post("/auth/register", json={
        "email": email, 
        "password": password,
        "full_name": "Test User"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == email
    assert data["is_active"] == True
    
    # Login with credentials
    token_resp = client.post(
        "/auth/login", 
        data={"username": email, "password": password}, 
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert token_resp.status_code == 200
    token_data = token_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_invalid_login(client: TestClient):
    """Test login with invalid credentials."""
    resp = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 401
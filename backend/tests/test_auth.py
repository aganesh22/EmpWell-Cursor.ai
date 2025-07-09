import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_register_and_login():
    email = "testuser@example.com"
    password = "secret123"
    resp = client.post("/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 201
    token_resp = client.post(
        "/auth/login", data={"username": email, "password": password}, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert token_resp.status_code == 200
    assert "access_token" in token_resp.json()
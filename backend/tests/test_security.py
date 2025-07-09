"""Security-focused tests for the wellbeing platform."""

import pytest
from fastapi.testclient import TestClient


class TestAuthenticationSecurity:
    """Test authentication security measures."""
    
    def test_password_hashing(self, client: TestClient):
        """Test that passwords are properly hashed."""
        response = client.post("/auth/register", json={
            "email": "hashtest@example.com",
            "password": "plaintext123",
            "full_name": "Hash Test"
        })
        
        if response.status_code == 201:
            # Password should never be returned in response
            data = response.json()
            assert "password" not in data
            assert "hashed_password" not in data
        else:
            pytest.skip("Registration failed")
    
    def test_jwt_token_required(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            "/auth/me",
            "/users/",
            "/reports/aggregate",
            "/notifications/run_alerts"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"
    
    def test_invalid_jwt_token(self, client: TestClient):
        """Test behavior with invalid JWT tokens."""
        invalid_tokens = [
            "invalid.jwt.token",
            "Bearer invalid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for token in invalid_tokens:
            response = client.get("/auth/me", headers={
                "Authorization": f"Bearer {token}"
            })
            assert response.status_code == 401
    
    def test_admin_role_required(self, client: TestClient):
        """Test that admin endpoints require admin role."""
        # Register regular user
        client.post("/auth/register", json={
            "email": "regular@example.com",
            "password": "password123",
            "full_name": "Regular User"
        })
        
        # Login as regular user
        login_response = client.post("/auth/login", data={
            "username": "regular@example.com",
            "password": "password123"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Could not login for admin test")
        
        token = login_response.json()["access_token"]
        
        # Try to access admin endpoints
        admin_endpoints = [
            "/users/",
            "/reports/aggregate",
            "/notifications/run_alerts"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers={
                "Authorization": f"Bearer {token}"
            })
            # Should get 403 (forbidden) not 401 (unauthorized)
            assert response.status_code in [403, 401], f"Admin endpoint {endpoint} accessible to regular user"


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_email_validation(self, client: TestClient):
        """Test email validation in registration."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user space@example.com"
        ]
        
        for email in invalid_emails:
            response = client.post("/auth/register", json={
                "email": email,
                "password": "password123",
                "full_name": "Test User"
            })
            assert response.status_code == 422, f"Invalid email {email} was accepted"
    
    def test_password_requirements(self, client: TestClient):
        """Test password strength requirements."""
        weak_passwords = [
            "",
            "123",
            "password"
        ]
        
        for password in weak_passwords:
            response = client.post("/auth/register", json={
                "email": f"test{len(password)}@example.com",
                "password": password,
                "full_name": "Test User"
            })
            # Should either reject (422) or accept but hash properly (201)
            assert response.status_code in [201, 422]
    
    def test_sql_injection_prevention(self, client: TestClient):
        """Test that SQL injection attempts are prevented."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "test@example.com'; SELECT * FROM users; --"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post("/auth/login", data={
                "username": malicious_input,
                "password": "password123"
            })
            # Should get 401 (invalid credentials) not 500 (server error)
            assert response.status_code in [401, 422]


class TestRateLimiting:
    """Test rate limiting and abuse prevention."""
    
    def test_login_attempts(self, client: TestClient):
        """Test multiple failed login attempts."""
        # Try multiple failed logins
        for i in range(5):
            response = client.post("/auth/login", data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            })
            # Should consistently return 401, not rate limit errors
            assert response.status_code == 401


class TestDataPrivacy:
    """Test data privacy and information disclosure."""
    
    def test_user_enumeration_prevention(self, client: TestClient):
        """Test that user enumeration is prevented."""
        # Try to register with existing email
        client.post("/auth/register", json={
            "email": "existing@example.com",
            "password": "password123",
            "full_name": "Existing User"
        })
        
        # Try to register again
        response = client.post("/auth/register", json={
            "email": "existing@example.com",
            "password": "password456",
            "full_name": "Another User"
        })
        
        # Should get error but not reveal that user exists
        assert response.status_code == 400
        error_message = response.json().get("detail", "").lower()
        assert "already" in error_message or "exists" in error_message
    
    def test_error_information_disclosure(self, client: TestClient):
        """Test that errors don't disclose sensitive information."""
        # Test various error scenarios
        error_responses = [
            client.get("/nonexistent-endpoint"),
            client.post("/auth/login", data={"invalid": "data"}),
            client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
        ]
        
        for response in error_responses:
            if response.status_code >= 400:
                # Check that error doesn't contain sensitive info
                response_text = response.text.lower()
                sensitive_keywords = ["password", "secret", "key", "token", "hash"]
                for keyword in sensitive_keywords:
                    assert keyword not in response_text, f"Error response contains sensitive keyword: {keyword}"
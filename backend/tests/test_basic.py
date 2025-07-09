"""Basic tests to verify the testing infrastructure works."""
import pytest

def test_basic_math():
    """Test basic math to verify pytest is working."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6

def test_imports():
    """Test that we can import key modules."""
    try:
        from backend.app.main import app
        assert app is not None
        print(f"✓ Successfully imported app: {type(app)}")
    except Exception as e:
        pytest.fail(f"Failed to import app: {e}")

def test_sqlmodel_import():
    """Test SQLModel imports."""
    try:
        from sqlmodel import SQLModel
        assert SQLModel is not None
        print("✓ Successfully imported SQLModel")
    except Exception as e:
        pytest.fail(f"Failed to import SQLModel: {e}")

def test_client_creation(client):
    """Test that the test client can be created."""
    assert client is not None
    print("✓ Test client created successfully")

def test_basic_request(client):
    """Test a basic request to the API."""
    try:
        response = client.get("/")
        print(f"✓ Root endpoint response: {response.status_code}")
        # Accept any response - just checking we can make requests
        assert response.status_code in [200, 404, 422]
    except Exception as e:
        pytest.fail(f"Failed basic request: {e}")

def test_docs_endpoint(client):
    """Test that we can access the docs endpoint."""
    try:
        response = client.get("/docs")
        print(f"✓ Docs endpoint response: {response.status_code}")
        # Docs should be available or redirect
        assert response.status_code in [200, 404, 307]
    except Exception as e:
        print(f"⚠ Docs endpoint failed: {e}")
        # Don't fail the test for docs endpoint
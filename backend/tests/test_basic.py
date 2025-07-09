"""Basic tests to verify the testing infrastructure works."""

def test_basic_math():
    """Test basic math to verify pytest is working."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6

def test_app_import():
    """Test that we can import the FastAPI app."""
    from backend.app.main import app
    assert app is not None
    assert hasattr(app, 'routes')

def test_client_connection(client):
    """Test that the test client can make a request."""
    response = client.get("/docs")
    # Should get either 200 (docs page) or 404 (if docs disabled)
    assert response.status_code in [200, 404]
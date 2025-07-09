import pytest
import os
import tempfile
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import get_session

@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine using SQLite."""
    # Use in-memory SQLite database for tests
    database_url = "sqlite:///:memory:"
    
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Import all models to ensure they're registered
    try:
        from backend.app import models  # noqa: F401
    except ImportError:
        pass
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    return engine

@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session

@pytest.fixture
def client(test_session):
    """Create a test client with database session override."""
    def get_session_override():
        return test_session
    
    app.dependency_overrides[get_session] = get_session_override
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
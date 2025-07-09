import pytest
import os
import tempfile
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import get_session

@pytest.fixture(scope="session")
def test_engine():
    # Use temporary file for SQLite database
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Import all models to ensure they're registered
    from backend.app import models  # noqa: F401
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def test_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(test_session):
    def get_session_override():
        return test_session
    
    app.dependency_overrides[get_session] = get_session_override
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
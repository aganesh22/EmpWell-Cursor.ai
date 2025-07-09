import pytest
import os
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import get_session

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    yield engine
    os.unlink("./test.db")

@pytest.fixture
def test_session(test_engine):
    with Session(test_engine) as session:
        yield session

@pytest.fixture
def client(test_session):
    def get_session_override():
        return test_session
    
    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()
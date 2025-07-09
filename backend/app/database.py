from __future__ import annotations

import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/postgres")

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Create all tables (development only)."""
    import backend.app.models  # noqa: F401 – ensures model metadata is registered

    SQLModel.metadata.create_all(bind=engine)


def get_session() -> Session:  # Dependency for FastAPI routes
    with Session(engine) as session:
        yield session
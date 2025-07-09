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

    # Seed WHO-5 Wellbeing Index if not present
    from sqlmodel import Session, select
    from backend.app.models import TestTemplate, Question

    with Session(engine) as session:
        exists_stmt = select(TestTemplate).where(TestTemplate.key == "who5")
        if not session.exec(exists_stmt).first():
            template = TestTemplate(key="who5", name="WHO-5 Wellbeing Index", description="Measure current mental wellbeing (last 2 weeks)")
            session.add(template)
            session.commit()
            session.refresh(template)

            questions_text = [
                "I have felt cheerful and in good spirits",
                "I have felt calm and relaxed",
                "I have felt active and vigorous",
                "I woke up feeling fresh and rested",
                "My daily life has been filled with things that interest me",
            ]
            for index, text in enumerate(questions_text, start=1):
                q = Question(template_id=template.id, text=text, order=index)
                session.add(q)
            session.commit()


def get_session() -> Session:  # Dependency for FastAPI routes
    with Session(engine) as session:
        yield session
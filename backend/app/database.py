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
                "Woke up feeling fresh and rested",
                "My daily life has been filled with things that interest me",
            ]
            for index, text in enumerate(questions_text, start=1):
                q = Question(template_id=template.id, text=text, order=index)
                session.add(q)
            session.commit()

        # Seed MBTI test (simplified)
        exists_stmt = select(TestTemplate).where(TestTemplate.key == "mbti")
        if not session.exec(exists_stmt).first():
            t = TestTemplate(key="mbti", name="16 Personality Types", description="MBTI-inspired assessment (simplified)")
            session.add(t)
            session.commit(); session.refresh(t)

            mbti_questions = [
                ("You prefer to recharge alone after social events.", "IE", "I"),
                ("You gain energy from being the center of attention.", "IE", "E"),
                ("You focus on concrete details rather than abstract ideas.", "SN", "S"),
                ("You are imaginative rather than realistic.", "SN", "N"),
                ("You prioritize logic over feelings when making decisions.", "TF", "T"),
                ("You value empathy over analytical thinking.", "TF", "F"),
                ("You like to have matters settled in advance.", "JP", "J"),
                ("You prefer to keep options open.", "JP", "P"),
            ]
            order = 1
            for text, pair, pos in mbti_questions:
                q = Question(
                    template_id=t.id,
                    text=text,
                    order=order,
                    min_value=1,
                    max_value=5,
                    dimension_pair=pair,
                    positive_letter=pos,
                )
                session.add(q)
                order += 1
            session.commit()

        # Seed DISC test (simplified)
        exists_stmt = select(TestTemplate).where(TestTemplate.key == "disc")
        if not session.exec(exists_stmt).first():
            t = TestTemplate(key="disc", name="DISC Assessment", description="Dominance, Influence, Steadiness, Conscientiousness (simplified)")
            session.add(t)
            session.commit(); session.refresh(t)

            disc_questions = [
                ("I enjoy taking charge and achieving goals.", "D", "D"),
                ("I am enthusiastic and like persuading others.", "I", "I"),
                ("I am patient and a good listener.", "S", "S"),
                ("I pay attention to accuracy and details.", "C", "C"),
            ]
            order = 1
            for text, pair, pos in disc_questions:
                q = Question(
                    template_id=t.id,
                    text=text,
                    order=order,
                    min_value=1,
                    max_value=5,
                    dimension_pair=pair,
                    positive_letter=pos,
                )
                session.add(q); order += 1
            session.commit()


def get_session() -> Session:  # Dependency for FastAPI routes
    with Session(engine) as session:
        yield session
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
                # I–E (8)
                ("I feel drained after extended socializing.", "IE", "I"),
                ("I speak up easily in large groups.", "IE", "E"),
                ("I prefer solitary activities to group ones.", "IE", "I"),
                ("Being around people energizes me.", "IE", "E"),
                ("I need quiet time to reflect on my thoughts.", "IE", "I"),
                ("I enjoy being the life of the party.", "IE", "E"),
                ("I find small talk exhausting.", "IE", "I"),
                ("I often start conversations with strangers.", "IE", "E"),
                # S–N (8)
                ("I trust facts more than ideas.", "SN", "S"),
                ("I enjoy brainstorming possibilities.", "SN", "N"),
                ("I notice details others miss.", "SN", "S"),
                ("I like to imagine future scenarios.", "SN", "N"),
                ("I prefer practical solutions to theoretical ones.", "SN", "S"),
                ("I'm drawn to abstract concepts.", "SN", "N"),
                ("I focus on current realities rather than possibilities.", "SN", "S"),
                ("I interpret patterns and meanings in events.", "SN", "N"),
                # T–F (8)
                ("I believe justice is more important than mercy.", "TF", "T"),
                ("I consider people's feelings before decisions.", "TF", "F"),
                ("Logical analysis comes naturally to me.", "TF", "T"),
                ("Maintaining harmony guides my actions.", "TF", "F"),
                ("I enjoy solving problems with objective criteria.", "TF", "T"),
                ("I empathize with others' emotions easily.", "TF", "F"),
                ("I value consistency over compassion.", "TF", "T"),
                ("I prioritize relationships over tasks.", "TF", "F"),
                # J–P (8)
                ("I like to have a detailed schedule.", "JP", "J"),
                ("I keep my options open until the last moment.", "JP", "P"),
                ("Planning ahead gives me comfort.", "JP", "J"),
                ("I'm spontaneous and flexible with plans.", "JP", "P"),
                ("I finish tasks before relaxing.", "JP", "J"),
                ("I work best close to deadlines.", "JP", "P"),
                ("I feel uneasy without clear closure.", "JP", "J"),
                ("I enjoy adapting to unexpected situations.", "JP", "P"),
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
                # Dominance 7
                ("I take charge in group situations.", "D", "D"),
                ("I enjoy competitive environments.", "D", "D"),
                ("I make quick decisions with confidence.", "D", "D"),
                ("I challenge obstacles head-on.", "D", "D"),
                ("I set ambitious goals for myself.", "D", "D"),
                ("I assert my opinions strongly.", "D", "D"),
                ("I thrive under pressure to achieve results.", "D", "D"),
                # Influence 7
                ("I enjoy networking with new people.", "I", "I"),
                ("I motivate others with enthusiasm.", "I", "I"),
                ("I have a persuasive communication style.", "I", "I"),
                ("I maintain an upbeat attitude.", "I", "I"),
                ("I enjoy being recognized publicly.", "I", "I"),
                ("I inspire team spirit in groups.", "I", "I"),
                ("I prefer collaborative over solitary work.", "I", "I"),
                # Steadiness 7
                ("I am patient even under stress.", "S", "S"),
                ("I value harmony in relationships.", "S", "S"),
                ("I am a good listener.", "S", "S"),
                ("I provide stable support to others.", "S", "S"),
                ("I prefer consistent routines.", "S", "S"),
                ("I remain calm in difficult situations.", "S", "S"),
                ("I am loyal to my team.", "S", "S"),
                # Conscientiousness 7
                ("I double-check details for accuracy.", "C", "C"),
                ("I follow established rules carefully.", "C", "C"),
                ("I prefer clear procedures and standards.", "C", "C"),
                ("I analyze information before acting.", "C", "C"),
                ("I strive for high quality in my work.", "C", "C"),
                ("I ask clarifying questions to avoid errors.", "C", "C"),
                ("I organize data systematically.", "C", "C"),
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
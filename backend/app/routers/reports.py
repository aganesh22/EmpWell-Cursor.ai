from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from backend.app.database import get_session
from backend.app.deps import require_admin
from backend.app.models import TestTemplate, TestAttempt

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/aggregate")
def aggregate_reports(admin=Depends(require_admin), session: Session = Depends(get_session)):
    data = {}

    # WHO-5 average
    who_template = session.exec(select(TestTemplate).where(TestTemplate.key == "who5")).first()
    if who_template:
        avg_score = session.exec(
            select(func.avg(TestAttempt.normalized_score)).where(TestAttempt.template_id == who_template.id)
        ).first()
        count = session.exec(select(func.count()).where(TestAttempt.template_id == who_template.id)).first()
        data["who5"] = {"average": round(avg_score or 0, 2), "n": count}

    # MBTI counts
    mbti_t = session.exec(select(TestTemplate).where(TestTemplate.key == "mbti")).first()
    if mbti_t:
        rows = session.exec(select(TestAttempt.interpretation).where(TestAttempt.template_id == mbti_t.id)).all()
        types = [r.split(": ")[-1] for r in rows if r]
        data["mbti"] = dict(Counter(types))

    # DISC counts
    disc_t = session.exec(select(TestTemplate).where(TestTemplate.key == "disc")).first()
    if disc_t:
        rows = session.exec(select(TestAttempt.interpretation).where(TestAttempt.template_id == disc_t.id)).all()
        cats = [r.split(": ")[-1] for r in rows if r]
        data["disc"] = dict(Counter(cats))

    return data
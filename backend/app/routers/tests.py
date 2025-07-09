from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.app.database import get_session
from backend.app.deps import get_current_user
from backend.app.models import TestTemplate, Question, TestAttempt, Response
from backend.app.schemas import TestTemplateRead, TestResult

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("/", response_model=List[TestTemplateRead])
def list_tests(session: Session = Depends(get_session)):
    templates = session.exec(select(TestTemplate)).all()
    return templates


@router.get("/{key}", response_model=TestTemplateRead)
def get_test(key: str, session: Session = Depends(get_session)):
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    return template


class SubmissionBody(TestResult):
    answers: List[int]  # keep for docs (not used in schema response)


@router.post("/{key}/submit", response_model=TestResult)
def submit_test(key: str, answers: List[int],  # Expect list of selected values in question order
                user=Depends(get_current_user), session: Session = Depends(get_session)):
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")

    questions = sorted(template.questions, key=lambda q: q.order)
    if len(answers) != len(questions):
        raise HTTPException(status_code=400, detail="Invalid number of answers")

    # Save attempt
    attempt = TestAttempt(template_id=template.id, user_id=user.id)
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    raw_score = 0.0
    for q, val in zip(questions, answers):
        if not (q.min_value <= val <= q.max_value):
            raise HTTPException(status_code=400, detail="Answer value out of range")
        raw_score += val * q.weight
        session.add(Response(attempt_id=attempt.id, question_id=q.id, value=val))

    # WHO-5 scoring
    normalized = raw_score * 4  # percentage 0-100
    # interpretation
    if normalized < 50:
        interp = "Low wellbeing (possible depression)"
    elif normalized < 75:
        interp = "Moderate wellbeing"
    else:
        interp = "High wellbeing"

    attempt.raw_score = raw_score
    attempt.normalized_score = normalized
    session.add(attempt)
    session.commit()

    return TestResult(raw_score=raw_score, normalized_score=normalized, interpretation=interp)
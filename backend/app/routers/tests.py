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

    if key == "who5":
        normalized = raw_score * 4  # 0-100
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

    elif key == "mbti":
        # accumulate per dimension
        dims = {"IE": 0, "SN": 0, "TF": 0, "JP": 0}
        for q, val in zip(questions, answers):
            pair = q.dimension_pair
            if not pair:
                continue
            positivity = q.positive_letter
            # if val <=3 choose positive else other letter
            if val <= 3:
                chosen = positivity
            else:
                chosen = pair.replace(positivity, "")
            dims[pair] += 1 if chosen == positivity else -1

        type_letters = "".join([
            (pair[0] if score > 0 else pair[1]) if pair in dims else "?"
            for pair, score in dims.items()
        ])
        interp = f"Your personality type: {type_letters}"
        attempt.raw_score = 0
        attempt.normalized_score = 0
        session.add(attempt)
        session.commit()
        return TestResult(raw_score=0, normalized_score=0, interpretation=interp)

    elif key == "disc":
        cats = {"D": 0, "I": 0, "S": 0, "C": 0}
        for q, val in zip(questions, answers):
            letter = q.positive_letter or ""
            cats[letter] += val
        dominant = max(cats, key=cats.get)
        interp = f"Your dominant DISC style: {dominant}"
        attempt.raw_score = 0
        attempt.normalized_score = 0
        session.add(attempt)
        session.commit()
        return TestResult(raw_score=0, normalized_score=0, interpretation=interp)

    else:
        raise HTTPException(status_code=400, detail="Scoring not implemented")
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
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
        tips = [
            "Consider small daily activities that bring you joy.",
            "Engage in relaxation techniques like deep breathing or meditation.",
            "Maintain a consistent sleep schedule to improve restfulness.",
        ]

        attempt.raw_score = raw_score
        attempt.normalized_score = normalized
        attempt.interpretation = interp
        session.add(attempt)
        session.commit()
        return TestResult(raw_score=raw_score, normalized_score=normalized, interpretation=interp, tips=tips)

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
        descriptions_mbti = {
            "INTJ": {
                "summary": "Strategic, insightful and independent.",
                "tips": [
                    "Set long-term goals and map backward steps.",
                    "Share your vision with stakeholders to gain buy-in.",
                ],
            },
            "INTP": {
                "summary": "Analytical, conceptual and inventive.",
                "tips": [
                    "Schedule time to turn ideas into action.",
                    "Explain your logic in simple language for others.",
                ],
            },
            "ENTJ": {"summary": "Decisive leaders, drive change.", "tips": ["Delegate details to stay strategic.", "Pause to consider team morale before acting."]},
            "ENTP": {"summary": "Visionary debaters, love innovation.", "tips": ["Close the loop on projects you start.", "Listen actively to opposing views."]},
            # … other 12 types omitted for brevity …
        }

        desc = descriptions_mbti.get(type_letters, {"summary": "Blend of preferences.", "tips": []})
        interp = f"{type_letters}: {desc['summary']}"
        tips = desc["tips"]

        attempt.raw_score = 0
        attempt.normalized_score = 0
        attempt.interpretation = interp
        session.add(attempt)
        session.commit()
        return TestResult(raw_score=0, normalized_score=0, interpretation=interp, tips=[t for t in tips if t])

    elif key == "disc":
        cats = {"D": 0, "I": 0, "S": 0, "C": 0}
        for q, val in zip(questions, answers):
            letter = q.positive_letter or ""
            cats[letter] += val
        dominant = max(cats, key=cats.get)
        interp = f"Your dominant DISC style: {dominant}"
        desc_disc = {
            "D": {
                "summary": "Direct, results-oriented and competitive.",
                "tips": [
                    "Practice active listening to build rapport.",
                    "Celebrate team achievements, not just results.",
                ],
            },
            "I": {
                "summary": "Influential, enthusiastic and persuasive.",
                "tips": [
                    "Organise your ideas before presenting.",
                    "Follow through on agreed actions.",
                ],
            },
            "S": {
                "summary": "Supportive, steady and cooperative.",
                "tips": [
                    "Voice your own needs and boundaries.",
                    "Embrace change in small, planned steps.",
                ],
            },
            "C": {
                "summary": "Conscientious, accurate and analytical.",
                "tips": [
                    "Accept ‘good-enough’ when time-boxed.",
                    "Share your expertise to help the team learn.",
                ],
            },
        }
        desc = desc_disc[dominant]
        interp = f"{interp} – {desc['summary']}"
        return TestResult(raw_score=0, normalized_score=0, interpretation=interp, tips=desc["tips"])

    else:
        raise HTTPException(status_code=400, detail="Scoring not implemented")


@router.get("/attempts/{attempt_id}/report", response_class=StreamingResponse)
def download_report(attempt_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    attempt = session.get(TestAttempt, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    # Only the owner or admin can download
    if attempt.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    template = session.get(TestTemplate, attempt.template_id)

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flow = []

    flow.append(Paragraph(f"{template.name} – Personal Report", styles["Title"]))
    flow.append(Paragraph(f"Date: {attempt.created_at.strftime('%Y-%m-%d')}", styles["Normal"]))
    flow.append(Spacer(1, 12))
    flow.append(Paragraph(f"Interpretation: <b>{attempt.interpretation or 'N/A'}</b>", styles["Heading2"]))

    if attempt.normalized_score is not None:
        flow.append(Paragraph(f"Overall Score: {attempt.normalized_score:.2f}", styles["Normal"]))

    # Tips
    from backend.app.schemas import TestResult

    if attempt.interpretation:
        result = TestResult.parse_obj({
            "raw_score": attempt.raw_score or 0,
            "normalized_score": attempt.normalized_score or 0,
            "interpretation": attempt.interpretation,
            "tips": [],
        })
    try:
        tips = result.tips  # type: ignore
        if tips:
            flow.append(Spacer(1, 12))
            flow.append(Paragraph("Recommendations:", styles["Heading3"]))
            for tip in tips:
                flow.append(Paragraph(f"• {tip}", styles["Normal"]))
    except Exception:
        pass

    # Simple bar chart for WHO-5 answers
    if template.key == "who5" and attempt.responses:
        values = [r.value for r in attempt.responses]
        drawing = Drawing(400, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 30
        bc.height = 130
        bc.width = 300
        bc.data = [values]
        bc.barWidth = 15
        bc.categoryAxis.categoryNames = [f"Q{i+1}" for i in range(len(values))]
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 5
        drawing.add(bc)
        flow.append(Spacer(1, 12))
        flow.append(drawing)

    doc.build(flow)

    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{attempt_id}.pdf"})
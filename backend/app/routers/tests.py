from __future__ import annotations

from typing import List, Dict, Any
import json

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

# Enhanced test library with comprehensive assessments
COMPREHENSIVE_TEST_LIBRARY = {
    "who5": {
        "key": "who5",
        "name": "WHO-5 Wellbeing Index",
        "description": "A short questionnaire to measure current mental wellbeing",
        "category": "wellbeing",
        "duration_minutes": 2,
        "branching_enabled": False,
        "questions": [
            {
                "id": 1, "text": "I have felt cheerful and in good spirits", "order": 1,
                "min_value": 0, "max_value": 5, "weight": 1.0, "question_type": "likert",
                "options": ["At no time", "Some of the time", "Less than half of the time", 
                           "More than half of the time", "Most of the time", "All of the time"],
                "required": True, "reverse_scored": False
            },
            {
                "id": 2, "text": "I have felt calm and relaxed", "order": 2,
                "min_value": 0, "max_value": 5, "weight": 1.0, "question_type": "likert",
                "options": ["At no time", "Some of the time", "Less than half of the time", 
                           "More than half of the time", "Most of the time", "All of the time"],
                "required": True, "reverse_scored": False
            },
            {
                "id": 3, "text": "I have felt active and vigorous", "order": 3,
                "min_value": 0, "max_value": 5, "weight": 1.0, "question_type": "likert",
                "options": ["At no time", "Some of the time", "Less than half of the time", 
                           "More than half of the time", "Most of the time", "All of the time"],
                "required": True, "reverse_scored": False
            },
            {
                "id": 4, "text": "I woke up feeling fresh and rested", "order": 4,
                "min_value": 0, "max_value": 5, "weight": 1.0, "question_type": "likert",
                "options": ["At no time", "Some of the time", "Less than half of the time", 
                           "More than half of the time", "Most of the time", "All of the time"],
                "required": True, "reverse_scored": False
            },
            {
                "id": 5, "text": "My daily life has been filled with things that interest me", "order": 5,
                "min_value": 0, "max_value": 5, "weight": 1.0, "question_type": "likert",
                "options": ["At no time", "Some of the time", "Less than half of the time", 
                           "More than half of the time", "Most of the time", "All of the time"],
                "required": True, "reverse_scored": False
            }
        ],
        "scoring_rules": {
            "type": "simple_sum",
            "normalization_method": "percentage"
        },
        "interpretation_guide": {
            "score_ranges": [
                {"min_score": 0, "max_score": 50, "label": "Poor Wellbeing", 
                 "description": "Indicates possible depression or low mood", "color": "#dc3545"},
                {"min_score": 51, "max_score": 75, "label": "Moderate Wellbeing", 
                 "description": "Some areas for improvement", "color": "#ffc107"},
                {"min_score": 76, "max_score": 100, "label": "High Wellbeing", 
                 "description": "Good mental wellbeing", "color": "#28a745"}
            ],
            "recommendations": [
                {"condition": "score < 50", 
                 "recommendations": ["Consider speaking with a mental health professional", 
                                  "Practice mindfulness and self-care", "Establish a regular sleep schedule"]},
                {"condition": "score >= 50 && score < 76", 
                 "recommendations": ["Incorporate regular exercise", "Connect with friends and family", 
                                  "Try stress management techniques"]},
                {"condition": "score >= 76", 
                 "recommendations": ["Maintain your current positive habits", 
                                  "Consider helping others who may be struggling"]}
            ],
            "risk_indicators": [
                {"question_ids": [1, 2, 3, 4, 5], "threshold_values": [1, 1, 1, 1, 1], 
                 "risk_level": "high", "alert_message": "Multiple low scores indicate significant wellbeing concerns"}
            ]
        }
    },
    "gad7": {
        "key": "gad7",
        "name": "GAD-7 Anxiety Assessment",
        "description": "Generalized Anxiety Disorder 7-item scale to measure anxiety symptoms",
        "category": "wellbeing",
        "duration_minutes": 3,
        "branching_enabled": True,
        "questions": [
            {
                "id": 11, "text": "Feeling nervous, anxious, or on edge", "order": 1,
                "min_value": 0, "max_value": 3, "weight": 1.0, "question_type": "likert",
                "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"],
                "required": True, "reverse_scored": False
            },
            {
                "id": 12, "text": "Not being able to stop or control worrying", "order": 2,
                "min_value": 0, "max_value": 3, "weight": 1.0, "question_type": "likert",
                "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"],
                "required": True, "reverse_scored": False
            },
            {
                "id": 18, "text": "If you checked off any problems, how difficult have these made it for you to do your work, take care of things at home, or get along with other people?", 
                "order": 8, "min_value": 0, "max_value": 3, "weight": 0.0, "question_type": "choice",
                "options": ["Not difficult at all", "Somewhat difficult", "Very difficult", "Extremely difficult"],
                "required": False, "show_if_question_id": 11, "show_if_value": 1, "reverse_scored": False
            }
        ],
        "scoring_rules": {"type": "simple_sum", "normalization_method": "percentage"},
        "interpretation_guide": {
            "score_ranges": [
                {"min_score": 0, "max_score": 4, "label": "Minimal Anxiety", "color": "#28a745"},
                {"min_score": 5, "max_score": 9, "label": "Mild Anxiety", "color": "#ffc107"},
                {"min_score": 10, "max_score": 14, "label": "Moderate Anxiety", "color": "#fd7e14"},
                {"min_score": 15, "max_score": 21, "label": "Severe Anxiety", "color": "#dc3545"}
            ],
            "recommendations": [],
            "risk_indicators": []
        }
    },
    "phq9": {
        "key": "phq9",
        "name": "PHQ-9 Depression Screening",
        "description": "Patient Health Questionnaire-9 for depression screening",
        "category": "wellbeing",
        "duration_minutes": 4,
        "branching_enabled": True,
        "questions": [
            {
                "id": 21, "text": "Little interest or pleasure in doing things", "order": 1,
                "min_value": 0, "max_value": 3, "weight": 1.0, "question_type": "likert",
                "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"],
                "required": True, "reverse_scored": False
            },
            {
                "id": 29, "text": "Thoughts that you would be better off dead, or of hurting yourself in some way", "order": 9,
                "min_value": 0, "max_value": 3, "weight": 1.0, "question_type": "likert",
                "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"],
                "required": True, "reverse_scored": False
            }
        ],
        "scoring_rules": {"type": "simple_sum", "normalization_method": "percentage"},
        "interpretation_guide": {
            "score_ranges": [
                {"min_score": 0, "max_score": 4, "label": "Minimal Depression", "color": "#28a745"},
                {"min_score": 20, "max_score": 27, "label": "Severe Depression", "color": "#6f42c1"}
            ],
            "recommendations": [],
            "risk_indicators": [
                {"question_ids": [29], "threshold_values": [1], "risk_level": "high", 
                 "alert_message": "CRITICAL: Suicidal ideation detected", 
                 "immediate_action": "Contact emergency services or crisis hotline"}
            ]
        }
    },
    "big5": {
        "key": "big5",
        "name": "Big Five Personality Assessment",
        "description": "Comprehensive personality assessment based on the Five-Factor Model",
        "category": "personality",
        "duration_minutes": 15,
        "branching_enabled": False,
        "questions": [
            {
                "id": 101, "text": "I see myself as someone who is original, comes up with new ideas", "order": 1,
                "min_value": 1, "max_value": 5, "weight": 1.0, "dimension_pair": "O", "positive_letter": "O",
                "question_type": "likert",
                "options": ["Disagree strongly", "Disagree a little", "Neither agree nor disagree", 
                           "Agree a little", "Agree strongly"],
                "required": True, "reverse_scored": False
            }
        ],
        "scoring_rules": {
            "type": "dimensional",
            "dimensions": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
        },
        "interpretation_guide": {"score_ranges": [], "recommendations": [], "risk_indicators": []}
    },
    "pss": {
        "key": "pss",
        "name": "Perceived Stress Scale",
        "description": "Measures the degree to which situations in life are perceived as stressful",
        "category": "stress",
        "duration_minutes": 5,
        "branching_enabled": False,
        "questions": [
            {
                "id": 201, "text": "In the last month, how often have you been upset because of something that happened unexpectedly?", 
                "order": 1, "min_value": 0, "max_value": 4, "weight": 1.0, "question_type": "likert",
                "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"],
                "required": True, "reverse_scored": False
            }
        ],
        "scoring_rules": {"type": "simple_sum", "normalization_method": "percentage"},
        "interpretation_guide": {"score_ranges": [], "recommendations": [], "risk_indicators": []}
    }
}


@router.get("/", response_model=List[Dict[str, Any]])
def list_tests(session: Session = Depends(get_session)):
    """Get all available tests from comprehensive library"""
    # Return tests from our comprehensive library
    return list(COMPREHENSIVE_TEST_LIBRARY.values())


@router.get("/{key}", response_model=Dict[str, Any])
def get_test(key: str, session: Session = Depends(get_session)):
    """Get a specific test by key"""
    if key in COMPREHENSIVE_TEST_LIBRARY:
        return COMPREHENSIVE_TEST_LIBRARY[key]
    
    # Fallback to database lookup for legacy tests
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    return template


def evaluate_branching_condition(responses: Dict[int, Any], question: Dict[str, Any]) -> bool:
    """Evaluate if a question should be shown based on branching conditions"""
    if not question.get("show_if_question_id") or question.get("show_if_value") is None:
        return True
    
    condition_response = responses.get(question["show_if_question_id"])
    if condition_response is None:
        return False
    
    return condition_response >= question["show_if_value"]


def calculate_advanced_score(test_config: Dict[str, Any], responses: List[int]) -> Dict[str, Any]:
    """Calculate test results using advanced scoring algorithms"""
    questions = test_config["questions"]
    scoring_rules = test_config["scoring_rules"]
    interpretation_guide = test_config["interpretation_guide"]
    
    # Filter responses for scoring (exclude non-scored questions)
    scored_responses = []
    response_map = {}
    
    for i, question in enumerate(questions):
        if i < len(responses) and question.get("weight", 1.0) > 0:
            value = responses[i]
            
            # Handle reverse scoring
            if question.get("reverse_scored", False):
                value = question["max_value"] - value + question["min_value"]
            
            scored_responses.append(value * question.get("weight", 1.0))
            response_map[question["id"]] = responses[i]
    
    raw_score = sum(scored_responses)
    
    # Normalize score based on method
    if scoring_rules.get("normalization_method") == "percentage":
        max_possible = sum(q["max_value"] * q.get("weight", 1.0) for q in questions if q.get("weight", 1.0) > 0)
        normalized_score = (raw_score / max_possible) * 100 if max_possible > 0 else 0
    else:
        normalized_score = raw_score
    
    # Get interpretation
    interpretation = "Score calculated"
    for score_range in interpretation_guide.get("score_ranges", []):
        if score_range["min_score"] <= normalized_score <= score_range["max_score"]:
            interpretation = score_range["label"]
            break
    
    # Get recommendations
    recommendations = []
    for rec_rule in interpretation_guide.get("recommendations", []):
        condition = rec_rule.get("condition", "")
        try:
            # Simple condition evaluation (replace 'score' with actual value)
            if eval(condition.replace("score", str(normalized_score))):
                recommendations.extend(rec_rule.get("recommendations", []))
        except:
            pass
    
    # Assess risk level
    risk_level = "low"
    for risk_indicator in interpretation_guide.get("risk_indicators", []):
        question_ids = risk_indicator.get("question_ids", [])
        threshold_values = risk_indicator.get("threshold_values", [])
        
        risk_triggered = False
        for i, q_id in enumerate(question_ids):
            if q_id in response_map:
                threshold = threshold_values[i] if i < len(threshold_values) else threshold_values[0]
                if response_map[q_id] >= threshold:
                    risk_triggered = True
                    break
        
        if risk_triggered:
            risk_level = risk_indicator.get("risk_level", "low")
            if risk_level == "high":
                break  # Immediate return for high risk
    
    return {
        "raw_score": raw_score,
        "normalized_score": normalized_score,
        "interpretation": interpretation,
        "tips": recommendations[:3],  # Limit to top 3 recommendations
        "risk_level": risk_level,
        "detailed_feedback": f"Your score indicates {interpretation.lower()}",
        "follow_up_suggested": risk_level in ["moderate", "high"] or normalized_score < 50
    }


@router.post("/{key}/submit", response_model=Dict[str, Any])
def submit_test(key: str, answers: List[int],
                user=Depends(get_current_user), session: Session = Depends(get_session)):
    """Submit test answers with enhanced scoring"""
    
    # Check if test exists in comprehensive library
    if key in COMPREHENSIVE_TEST_LIBRARY:
        test_config = COMPREHENSIVE_TEST_LIBRARY[key]
        
        # Calculate results using advanced scoring
        results = calculate_advanced_score(test_config, answers)
        
        # Save attempt to database (optional for tracking)
        try:
            # Try to find or create template in database
            template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
            if not template:
                # Create minimal template for tracking
                template = TestTemplate(key=key, name=test_config["name"])
                session.add(template)
                session.commit()
                session.refresh(template)
            
            # Save attempt
            attempt = TestAttempt(
                template_id=template.id, 
                user_id=user.id,
                raw_score=results["raw_score"],
                normalized_score=results["normalized_score"],
                interpretation=results["interpretation"]
            )
            session.add(attempt)
            session.commit()
            session.refresh(attempt)
            
            # Save responses
            for i, answer in enumerate(answers):
                if i < len(test_config["questions"]):
                    question_id = test_config["questions"][i]["id"]
                    response = Response(
                        attempt_id=attempt.id,
                        question_id=question_id,  # Using virtual question ID
                        value=answer
                    )
                    session.add(response)
            
            session.commit()
            
        except Exception as e:
            # Continue even if database save fails
            print(f"Warning: Could not save attempt to database: {e}")
        
        return results
    
    # Fallback to legacy test handling
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")

    questions = sorted(template.questions, key=lambda q: q.order)
    if len(answers) > len(questions):
        raise HTTPException(status_code=400, detail="Too many answers supplied")

    # Save attempt
    attempt = TestAttempt(template_id=template.id, user_id=user.id)
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    raw_score = 0.0
    answer_map: dict[int, int] = {}
    for idx, q in enumerate(questions):
        # Branching: if question has condition
        if q.show_if_question_id and q.show_if_value is not None:
            prev_val = answer_map.get(q.show_if_question_id)
            if prev_val != q.show_if_value:
                continue  # skip question

        if idx >= len(answers):
            raise HTTPException(status_code=400, detail="Missing answers for required questions")
        val = answers[idx]

        if not (q.min_value <= val <= q.max_value):
            raise HTTPException(status_code=400, detail="Answer value out of range")

        raw_score += val * q.weight
        answer_map[q.id] = val
        session.add(Response(attempt_id=attempt.id, question_id=q.id, value=val))

    # Legacy scoring for backward compatibility
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

    else:
        raise HTTPException(status_code=400, detail="Scoring not implemented for this test")


@router.get("/categories/{category}")
def get_tests_by_category(category: str):
    """Get tests filtered by category"""
    filtered_tests = [
        test for test in COMPREHENSIVE_TEST_LIBRARY.values() 
        if test.get("category") == category
    ]
    return filtered_tests


@router.get("/search/{query}")
def search_tests(query: str):
    """Search tests by name or description"""
    query_lower = query.lower()
    matching_tests = [
        test for test in COMPREHENSIVE_TEST_LIBRARY.values()
        if (query_lower in test.get("name", "").lower() or 
            query_lower in test.get("description", "").lower() or
            query_lower in test.get("key", "").lower())
    ]
    return matching_tests


# Keep existing PDF report generation
@router.get("/attempts/{attempt_id}/report", response_class=StreamingResponse)
def download_report(attempt_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    attempt = session.get(TestAttempt, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    # Only the owner or admin can download
    if attempt.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    template = session.get(TestTemplate, attempt.template_id)

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

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

    doc.build(flow)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", 
                           headers={"Content-Disposition": f"attachment; filename=report_{attempt_id}.pdf"})
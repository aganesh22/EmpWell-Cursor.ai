from __future__ import annotations

from typing import List, Dict, Any
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from sqlmodel import Session, select

from backend.app.database import get_session
from backend.app.deps import get_current_user
from backend.app.models import TestTemplate, Question, TestAttempt, Response
from backend.app.schemas import TestTemplateRead, TestResult
from backend.app.core.branching import (
    create_branching_controller,
    create_rules_processor,
    create_score_calculator,
    create_progress_tracker
)
from backend.app.core.standardized_tests import (
    StandardizedTestRegistry,
    WHO5WellbeingIndex,
    GAD7AnxietyScale,
    calculate_who5_score,
    calculate_gad7_score
)
from backend.app.core.personality_tests import PersonalityTest, calculate_personality_type

router = APIRouter(prefix="/tests", tags=["tests"])
logger = logging.getLogger(__name__)

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
    },
    "mbti16": {
        "key": "mbti16",
        "name": "16 Personality Types Assessment",
        "description": "MBTI-inspired personality assessment measuring four dichotomies",
        "category": "personality",
        "duration_minutes": 15,
        "branching_enabled": False,
        "questions": PersonalityTest.get_question_data(),
        "scoring_rules": {"type": "dimensional", "dimensions": ["EI", "SN", "TF", "JP"]},
        "interpretation_guide": {
            "score_ranges": [],
            "recommendations": [],
            "risk_indicators": [],
            "personality_types": list(PersonalityTest.TYPE_DESCRIPTIONS.keys())
        }
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
        
        # Special handling for personality test
        if key == "mbti16":
            try:
                personality_result = calculate_personality_type(answers)
                results = {
                    "raw_score": 0,  # Not applicable for personality test
                    "normalized_score": 0,  # Not applicable for personality test
                    "interpretation": str(personality_result.personality_type.value),
                    "personality_type": personality_result.personality_type.value,
                    "type_description": personality_result.type_description,
                    "dimension_scores": {k.value: v for k, v in personality_result.dimension_scores.items()},
                    "dimension_preferences": {k.value: v for k, v in personality_result.dimension_preferences.items()},
                    "confidence_scores": {k.value: v for k, v in personality_result.confidence_scores.items()},
                    "strengths": personality_result.strengths,
                    "potential_challenges": personality_result.potential_challenges,
                    "career_suggestions": personality_result.career_suggestions,
                    "relationship_insights": personality_result.relationship_insights,
                    "development_tips": personality_result.development_tips,
                    "tips": personality_result.development_tips[:3],  # For compatibility
                    "risk_level": "low",  # Personality tests don't have risk levels
                    "detailed_feedback": f"Your personality type is {personality_result.personality_type.value}",
                    "follow_up_suggested": False
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error calculating personality type: {str(e)}"
                )
        else:
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

    # Use branching logic for question evaluation
    controller = create_branching_controller(session)
    visible_questions = controller.get_visible_questions(template.id, [])
    
    if len(answers) > len(visible_questions):
        raise HTTPException(status_code=400, detail="Too many answers supplied")

    # Process answers with branching logic
    for idx, answer in enumerate(answers):
        if idx >= len(visible_questions):
            break
            
        question = visible_questions[idx]
        
        if not (question.min_value <= answer <= question.max_value):
            raise HTTPException(status_code=400, detail="Answer value out of range")

        # Save response
        response = Response(attempt_id=attempt.id, question_id=question.id, value=answer)
        session.add(response)
        session.commit()
        
        # Update visible questions after each answer (for branching)
        all_responses = session.exec(
            select(Response).where(Response.attempt_id == attempt.id)
        ).all()
        visible_questions = controller.get_visible_questions(template.id, all_responses)

    # Calculate final score using branching score calculator
    score_calculator = create_score_calculator(session)
    raw_score, normalized_score = score_calculator.calculate_test_score(attempt.id)

    # Legacy scoring for backward compatibility
    if key == "who5":
        # Use standardized WHO-5 implementation for better accuracy
        try:
            who5_result = calculate_who5_score(answers)
            attempt.raw_score = who5_result.raw_score
            attempt.normalized_score = who5_result.percentage_score
            attempt.interpretation = who5_result.description
            session.add(attempt)
            session.commit()
            
            return TestResult(
                raw_score=who5_result.raw_score,
                normalized_score=who5_result.percentage_score,
                interpretation=who5_result.description,
                tips=who5_result.recommendations[:3]  # Limit to 3 for legacy compatibility
            )
        except Exception as e:
            logger.warning(f"Standardized WHO-5 scoring failed, using legacy: {e}")
            # Fallback to legacy scoring
            if normalized_score < 50:
                interp = "Low wellbeing (possible depression)"
            elif normalized_score < 75:
                interp = "Moderate wellbeing"
            else:
                interp = "High wellbeing"
            tips = [
                "Consider small daily activities that bring you joy.",
                "Engage in relaxation techniques like deep breathing or meditation.",
                "Maintain a consistent sleep schedule to improve restfulness.",
            ]

            attempt.raw_score = raw_score
            attempt.normalized_score = normalized_score
            attempt.interpretation = interp
            session.add(attempt)
            session.commit()
            return TestResult(raw_score=raw_score, normalized_score=normalized_score, interpretation=interp, tips=tips)

    else:
        # For other tests, use the calculated scores
        attempt.raw_score = raw_score
        attempt.normalized_score = normalized_score
        attempt.interpretation = "Score calculated using branching logic"
        session.add(attempt)
        session.commit()
        return TestResult(
            raw_score=raw_score,
            normalized_score=normalized_score,
            interpretation="Score calculated using branching logic",
            tips=["Review your responses and consider areas for improvement."]
        )


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


# --- Standardized Tests Endpoints ---

@router.get("/standardized", response_model=List[Dict[str, Any]])
def list_standardized_tests():
    """Get all available standardized psychological tests"""
    return StandardizedTestRegistry.list_tests()


@router.get("/standardized/{key}", response_model=Dict[str, Any])
def get_standardized_test(key: str):
    """Get details for a specific standardized test"""
    test_class = StandardizedTestRegistry.get_test(key)
    if not test_class:
        raise HTTPException(status_code=404, detail="Standardized test not found")
    
    return {
        "key": test_class.KEY,
        "name": test_class.NAME,
        "version": test_class.VERSION,
        "administration_time": test_class.ADMINISTRATION_TIME,
        "question_count": len(test_class.QUESTIONS),
        "questions": test_class.get_question_data() if hasattr(test_class, 'get_question_data') else test_class.QUESTIONS,
        "description": f"Standardized {test_class.NAME} assessment",
        "scoring_info": {
            "type": "standardized",
            "validated": True,
            "normative_data": True
        }
    }


@router.post("/standardized/{key}/submit", response_model=Dict[str, Any])
def submit_standardized_test(
    key: str,
    responses: List[int],
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Submit responses for a standardized test and get detailed results"""
    test_class = StandardizedTestRegistry.get_test(key)
    if not test_class:
        raise HTTPException(status_code=404, detail="Standardized test not found")
    
    try:
        # Validate responses
        if hasattr(test_class, 'validate_response_set'):
            is_valid, errors = test_class.validate_response_set(responses)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid responses: {'; '.join(errors)}"
                )
        
        # Calculate score using the standardized algorithm
        result = test_class.calculate_score(responses)
        
        # Save to database for tracking
        try:
            # Get or create template
            template = session.exec(
                select(TestTemplate).where(TestTemplate.key == key)
            ).first()
            
            if not template:
                template = test_class.create_database_template(session)
            
            # Create attempt
            attempt = TestAttempt(
                template_id=template.id,
                user_id=user.id,
                raw_score=result.raw_score,
                normalized_score=result.percentage_score,
                interpretation=result.description
            )
            session.add(attempt)
            session.commit()
            session.refresh(attempt)
            
            # Save individual responses
            questions = session.exec(
                select(Question)
                .where(Question.template_id == template.id)
                .order_by(Question.order)
            ).all()
            
            for i, response_value in enumerate(responses):
                if i < len(questions):
                    response = Response(
                        attempt_id=attempt.id,
                        question_id=questions[i].id,
                        value=response_value
                    )
                    session.add(response)
            
            session.commit()
            
        except Exception as e:
            logger.warning(f"Failed to save standardized test attempt: {e}")
            # Continue with result even if database save fails
        
        # Return comprehensive results
        return {
            "test_key": key,
            "test_name": test_class.NAME,
            "version": test_class.VERSION,
            "completion_date": datetime.utcnow().isoformat(),
            "raw_score": result.raw_score,
            "percentage_score": result.percentage_score,
            "interpretation": result.interpretation.value,
            "risk_level": result.risk_level.value,
            "description": result.description,
            "recommendations": result.recommendations,
            "clinical_considerations": result.clinical_considerations,
            "follow_up_suggested": result.follow_up_suggested,
            "normative_percentile": result.normative_percentile,
            "attempt_id": attempt.id if 'attempt' in locals() else None
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing standardized test {key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing test submission"
        )


@router.get("/standardized/{key}/questions", response_model=List[Dict[str, Any]])
def get_standardized_test_questions(key: str):
    """Get questions for a standardized test"""
    test_class = StandardizedTestRegistry.get_test(key)
    if not test_class:
        raise HTTPException(status_code=404, detail="Standardized test not found")
    
    if hasattr(test_class, 'get_question_data'):
        return test_class.get_question_data()
    else:
        return test_class.QUESTIONS


@router.post("/standardized/init-templates")
def initialize_standardized_templates(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    """Initialize all standardized test templates in the database (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can initialize test templates"
        )
    
    try:
        templates = StandardizedTestRegistry.initialize_all_templates(session)
        
        return {
            "message": f"Successfully initialized {len(templates)} standardized test templates",
            "templates": [
                {
                    "key": template.key,
                    "name": template.name,
                    "id": template.id
                }
                for template in templates
            ]
        }
        
    except Exception as e:
        logger.error(f"Error initializing standardized templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initializing test templates"
        )


@router.get("/standardized/{key}/interpretation/{score}")
def get_score_interpretation(key: str, score: float):
    """Get interpretation for a specific score on a standardized test"""
    test_class = StandardizedTestRegistry.get_test(key)
    if not test_class:
        raise HTTPException(status_code=404, detail="Standardized test not found")
    
    # Create dummy responses to get interpretation
    if key == "who5":
        # WHO-5 percentage score, convert back to responses
        raw_score = int(score * 25 / 100)
        dummy_responses = [raw_score // 5] * 5  # Approximate equal distribution
    elif key == "gad7":
        # GAD-7 raw score
        raw_score = int(score)
        dummy_responses = [raw_score // 7] * 7  # Approximate equal distribution
    else:
        raise HTTPException(status_code=400, detail="Score interpretation not available for this test")
    
    try:
        result = test_class.calculate_score(dummy_responses)
        return {
            "score": score,
            "interpretation": result.interpretation.value,
            "risk_level": result.risk_level.value,
            "description": result.description,
            "normative_percentile": result.normative_percentile
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error interpreting score: {e}"
        )


# New Branching Logic Endpoints

@router.post("/{key}/start", response_model=Dict[str, Any])
def start_test_attempt(
    key: str,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Start a new test attempt with branching support"""
    # Check if test exists in comprehensive library
    if key in COMPREHENSIVE_TEST_LIBRARY:
        test_config = COMPREHENSIVE_TEST_LIBRARY[key]
        
        # Create or get template
        template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
        if not template:
            template = TestTemplate(
                key=key,
                name=test_config["name"],
                description=test_config.get("description", "")
            )
            session.add(template)
            session.commit()
            session.refresh(template)
        
        # Create new attempt
        attempt = TestAttempt(
            template_id=template.id,
            user_id=user.id
        )
        session.add(attempt)
        session.commit()
        session.refresh(attempt)
        
        return {
            "attempt_id": attempt.id,
            "template_key": key,
            "template_name": test_config["name"],
            "branching_enabled": test_config.get("branching_enabled", False)
        }
    
    # Fallback to legacy database templates
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    
    attempt = TestAttempt(template_id=template.id, user_id=user.id)
    session.add(attempt)
    session.commit()
    session.refresh(attempt)
    
    return {
        "attempt_id": attempt.id,
        "template_key": key,
        "template_name": template.name,
        "branching_enabled": True  # Assume database templates support branching
    }


@router.get("/{key}/question", response_model=Dict[str, Any])
def get_next_question(
    key: str,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get the next question in a test attempt using branching logic"""
    # Get the user's current attempt for this test
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    
    current_attempt = session.exec(
        select(TestAttempt)
        .where(TestAttempt.template_id == template.id)
        .where(TestAttempt.user_id == user.id)
        .order_by(TestAttempt.created_at.desc())
    ).first()
    
    if not current_attempt:
        raise HTTPException(status_code=404, detail="No active test attempt found. Please start the test first.")
    
    # Use branching controller to get next question
    controller = create_branching_controller(session)
    next_question = controller.get_next_question(current_attempt.id)
    
    if not next_question:
        raise HTTPException(status_code=404, detail="Test completed")
    
    # Get progress information
    progress_tracker = create_progress_tracker(session)
    progress = progress_tracker.get_test_progress(current_attempt.id)
    
    return {
        "id": next_question.id,
        "text": next_question.text,
        "order": next_question.order,
        "min_value": next_question.min_value,
        "max_value": next_question.max_value,
        "required": True,
        "progress": progress,
        "is_conditional": next_question.show_if_question_id is not None
    }


@router.post("/{key}/answer", response_model=Dict[str, Any])
def submit_answer(
    key: str,
    answer_data: Dict[str, Any],
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Submit an answer for the current question"""
    question_id = answer_data.get("question_id")
    value = answer_data.get("value")
    
    if question_id is None or value is None:
        raise HTTPException(status_code=400, detail="question_id and value are required")
    
    # Get the user's current attempt
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    
    current_attempt = session.exec(
        select(TestAttempt)
        .where(TestAttempt.template_id == template.id)
        .where(TestAttempt.user_id == user.id)
        .order_by(TestAttempt.created_at.desc())
    ).first()
    
    if not current_attempt:
        raise HTTPException(status_code=404, detail="No active test attempt found")
    
    # Validate the question exists and the value is in range
    question = session.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if not (question.min_value <= value <= question.max_value):
        raise HTTPException(status_code=400, detail="Answer value out of range")
    
    # Check if this question was already answered (prevent duplicates)
    existing_response = session.exec(
        select(Response)
        .where(Response.attempt_id == current_attempt.id)
        .where(Response.question_id == question_id)
    ).first()
    
    if existing_response:
        # Update existing response
        existing_response.value = value
        session.add(existing_response)
    else:
        # Create new response
        response = Response(
            attempt_id=current_attempt.id,
            question_id=question_id,
            value=value
        )
        session.add(response)
    
    session.commit()
    
    # Get next question using branching logic
    controller = create_branching_controller(session)
    next_question = controller.get_next_question(current_attempt.id)
    
    # Get updated progress
    progress_tracker = create_progress_tracker(session)
    progress = progress_tracker.get_test_progress(current_attempt.id)
    
    response_data = {
        "answer_recorded": True,
        "progress": progress,
        "test_complete": next_question is None
    }
    
    if next_question:
        response_data["next_question"] = {
            "id": next_question.id,
            "text": next_question.text,
            "order": next_question.order,
            "min_value": next_question.min_value,
            "max_value": next_question.max_value
        }
    
    return response_data


@router.get("/{key}/results", response_model=Dict[str, Any])
def get_test_results(
    key: str,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get results for a completed test with branching logic"""
    # Get the user's most recent completed attempt
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    
    current_attempt = session.exec(
        select(TestAttempt)
        .where(TestAttempt.template_id == template.id)
        .where(TestAttempt.user_id == user.id)
        .order_by(TestAttempt.created_at.desc())
    ).first()
    
    if not current_attempt:
        raise HTTPException(status_code=404, detail="No test attempt found")
    
    # Check if test is complete
    controller = create_branching_controller(session)
    next_question = controller.get_next_question(current_attempt.id)
    
    if next_question is not None:
        raise HTTPException(status_code=400, detail="Test not yet completed")
    
    # Calculate scores using branching logic
    score_calculator = create_score_calculator(session)
    raw_score, normalized_score = score_calculator.calculate_test_score(current_attempt.id)
    
    # Calculate dimensional scores if applicable
    dimensional_scores = score_calculator.calculate_dimensional_scores(current_attempt.id)
    
    # Get question path taken
    progress_tracker = create_progress_tracker(session)
    question_path = progress_tracker.get_question_path(current_attempt.id)
    
    # Update attempt with calculated scores
    current_attempt.raw_score = raw_score
    current_attempt.normalized_score = normalized_score
    
    # Generate interpretation
    interpretation = "Score calculated"
    if key in COMPREHENSIVE_TEST_LIBRARY:
        test_config = COMPREHENSIVE_TEST_LIBRARY[key]
        interpretation_guide = test_config.get("interpretation_guide", {})
        
        for score_range in interpretation_guide.get("score_ranges", []):
            if score_range["min_score"] <= normalized_score <= score_range["max_score"]:
                interpretation = score_range["label"]
                break
    
    current_attempt.interpretation = interpretation
    session.add(current_attempt)
    session.commit()
    
    return {
        "attempt_id": current_attempt.id,
        "raw_score": raw_score,
        "normalized_score": normalized_score,
        "interpretation": interpretation,
        "dimensional_scores": dimensional_scores,
        "question_path": question_path,
        "total_questions_answered": len(question_path),
        "test_completed_at": current_attempt.created_at.isoformat()
    }


@router.get("/{key}/progress", response_model=Dict[str, Any])
def get_test_progress(
    key: str,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current progress for an ongoing test"""
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    
    current_attempt = session.exec(
        select(TestAttempt)
        .where(TestAttempt.template_id == template.id)
        .where(TestAttempt.user_id == user.id)
        .order_by(TestAttempt.created_at.desc())
    ).first()
    
    if not current_attempt:
        raise HTTPException(status_code=404, detail="No active test attempt found")
    
    progress_tracker = create_progress_tracker(session)
    progress = progress_tracker.get_test_progress(current_attempt.id)
    
    return progress


@router.get("/{key}/validate", response_model=Dict[str, Any])
def validate_test_branching(
    key: str,
    session: Session = Depends(get_session)
):
    """Validate the branching rules for a test template"""
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    
    rules_processor = create_rules_processor(session)
    is_valid, errors = rules_processor.validate_branching_rules(template.id)
    
    return {
        "template_key": key,
        "is_valid": is_valid,
        "errors": errors,
        "validation_timestamp": "2024-01-01T00:00:00Z"  # Current timestamp would go here
    }


@router.get("/{key}/branching-tree", response_model=Dict[str, Any])
def get_branching_tree(
    key: str,
    session: Session = Depends(get_session)
):
    """Get the branching tree structure for a test"""
    template = session.exec(select(TestTemplate).where(TestTemplate.key == key)).first()
    if not template:
        raise HTTPException(status_code=404, detail="Test not found")
    
    rules_processor = create_rules_processor(session)
    tree = rules_processor.get_branching_tree(template.id)
    
    return tree


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


# ---------------------------------------------------------------------------
# Test Helper Wrappers
# ---------------------------------------------------------------------------
# The test suite expects certain standalone helper functions to be directly
# importable from ``backend.app.routers.tests``.  These wrappers delegate the
# actual work to the richer implementations that live inside
# ``backend.app.core.branching``.  Keeping them here avoids tight coupling
# between the tests and the core package structure while preventing
# ImportError failures when running the test suite.

from typing import List

from backend.app.core.branching import (
    create_branching_controller,
    create_score_calculator,
    create_rules_processor,
)


def should_show_question(question: Question, previous_responses: List[Response], session: Session):
    """Public wrapper around QuestionDisplayController.should_show_question."""
    controller = create_branching_controller(session)
    return controller.should_show_question(question, previous_responses)


def calculate_test_score(attempt_id: int, session: Session):
    """Return raw and normalized scores for the given attempt."""
    calculator = create_score_calculator(session)
    return calculator.calculate_test_score(attempt_id)


# Lightweight wrappers required by the test-suite --------------------------

def get_next_question(attempt_id: int, session: Session):
    """Return the next question for the given attempt using branching logic."""
    controller = create_branching_controller(session)
    return controller.get_next_question(attempt_id)


def get_test_progress(attempt_id: int, session: Session):
    """Return progress information for the given attempt."""
    from backend.app.core.branching import create_progress_tracker

    tracker = create_progress_tracker(session)
    return tracker.get_test_progress(attempt_id)


def validate_branching_rules(template_id: int, session: Session):
    """Validate branching rules and return (is_valid, errors)."""
    processor = create_rules_processor(session)
    return processor.validate_branching_rules(template_id)
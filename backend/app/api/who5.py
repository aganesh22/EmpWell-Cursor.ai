"""
API endpoints for WHO-5 Wellbeing Index Assessment.

This module provides REST API endpoints for administering and scoring the WHO-5 assessment.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from backend.app.database import get_session
from backend.app.models import TestTemplate, TestAttempt, Response, User
from backend.app.core.who5_assessment import WHO5Assessment, WHO5Result
from backend.app.deps import get_current_user

router = APIRouter(prefix="/who5", tags=["WHO-5 Assessment"])


class WHO5ResponseRequest(BaseModel):
    """Request model for WHO-5 assessment responses."""
    responses: List[int] = Field(
        ..., 
        description="List of 5 integers (0-5) representing responses to each question",
        min_items=5,
        max_items=5
    )


class WHO5ResultResponse(BaseModel):
    """Response model for WHO-5 assessment results."""
    raw_score: int
    percentage_score: int
    score_level: str
    
    # Detailed interpretation
    interpretation: str
    recommendations: List[str]
    risk_indicators: List[str]
    strengths: List[str]
    
    # Clinical insights
    depression_screening: str
    wellbeing_status: str
    follow_up_needed: bool
    
    # Individual question analysis
    question_scores: Dict[int, int]
    lowest_scoring_areas: List[str]
    highest_scoring_areas: List[str]


class WHO5QuestionResponse(BaseModel):
    """Response model for WHO-5 questions."""
    id: int
    text: str
    timeframe: str
    area: str
    response_scale: List[Dict[str, Any]]
    type: str
    required: bool
    min_value: int
    max_value: int


@router.get("/questions", response_model=List[WHO5QuestionResponse])
async def get_who5_questions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get WHO-5 assessment questions.
    
    Returns all 5 questions with their response scales for the WHO-5 assessment.
    """
    try:
        questions = WHO5Assessment.get_question_data()
        return [WHO5QuestionResponse(**q) for q in questions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve WHO-5 questions: {str(e)}"
        )


@router.post("/submit", response_model=WHO5ResultResponse)
async def submit_who5_assessment(
    request: WHO5ResponseRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Submit WHO-5 assessment responses and get results.
    
    Processes the user's responses to calculate their WHO-5 wellbeing score and returns
    comprehensive analysis including clinical insights and recommendations.
    """
    try:
        # Validate responses
        is_valid, errors = WHO5Assessment.validate_responses(request.responses)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid responses: {'; '.join(errors)}"
            )
        
        # Calculate WHO-5 score
        result = WHO5Assessment.calculate_who5_score(request.responses)
        
        # Get or create test template
        template = WHO5Assessment.create_database_template(session)
        
        # Create test attempt record
        test_attempt = TestAttempt(
            user_id=current_user.id,
            template_id=template.id,
            completed=True,
            score=result.percentage_score,
            interpretation=f"WHO-5 Score: {result.percentage_score}% ({result.score_level.value})"
        )
        session.add(test_attempt)
        session.commit()
        session.refresh(test_attempt)
        
        # Store individual responses
        for i, response_value in enumerate(request.responses):
            response = Response(
                attempt_id=test_attempt.id,
                question_id=None,  # We'll use question_order since we don't have individual question IDs
                question_order=i + 1,
                value=response_value,
                response_type="likert"
            )
            session.add(response)
        
        session.commit()
        
        # Return formatted result
        return WHO5ResultResponse(
            raw_score=result.raw_score,
            percentage_score=result.percentage_score,
            score_level=result.score_level.value,
            interpretation=result.interpretation,
            recommendations=result.recommendations,
            risk_indicators=result.risk_indicators,
            strengths=result.strengths,
            depression_screening=result.depression_screening,
            wellbeing_status=result.wellbeing_status,
            follow_up_needed=result.follow_up_needed,
            question_scores=result.question_scores,
            lowest_scoring_areas=result.lowest_scoring_areas,
            highest_scoring_areas=result.highest_scoring_areas
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process WHO-5 assessment: {str(e)}"
        )


@router.get("/info")
async def get_who5_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get general information about the WHO-5 assessment.
    
    Returns metadata about the assessment including name, description, and administration time.
    """
    return {
        "name": WHO5Assessment.NAME,
        "key": WHO5Assessment.KEY,
        "version": WHO5Assessment.VERSION,
        "administration_time": WHO5Assessment.ADMINISTRATION_TIME,
        "description": "The WHO-5 Well-Being Index is a short questionnaire consisting of 5 simple and non-invasive questions, which tap into subjective wellbeing. It measures current mental wellbeing over the past two weeks and has been validated as both a screening tool for depression and an outcome measure in clinical trials.",
        "question_count": len(WHO5Assessment.QUESTIONS),
        "response_format": "likert_scale",
        "scoring_method": "sum_and_multiply",
        "score_range": "0-100%",
        "depression_screening_threshold": WHO5Assessment.DEPRESSION_SCREENING_THRESHOLD,
        "clinical_use": "Depression screening and wellbeing monitoring"
    }


@router.get("/results/{attempt_id}", response_model=WHO5ResultResponse)
async def get_who5_results(
    attempt_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve previous WHO-5 assessment results.
    
    Returns the results of a previously completed WHO-5 assessment by attempt ID.
    """
    try:
        # Get test attempt
        attempt = session.exec(
            select(TestAttempt)
            .where(TestAttempt.id == attempt_id)
            .where(TestAttempt.user_id == current_user.id)
        ).first()
        
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="WHO-5 assessment attempt not found"
            )
        
        # Get responses
        responses = session.exec(
            select(Response)
            .where(Response.attempt_id == attempt_id)
            .order_by(Response.question_order)
        ).all()
        
        if len(responses) != 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incomplete response data found"
            )
        
        # Extract response values
        response_values = [response.value for response in responses]
        
        # Recalculate results
        result = WHO5Assessment.calculate_who5_score(response_values)
        
        return WHO5ResultResponse(
            raw_score=result.raw_score,
            percentage_score=result.percentage_score,
            score_level=result.score_level.value,
            interpretation=result.interpretation,
            recommendations=result.recommendations,
            risk_indicators=result.risk_indicators,
            strengths=result.strengths,
            depression_screening=result.depression_screening,
            wellbeing_status=result.wellbeing_status,
            follow_up_needed=result.follow_up_needed,
            question_scores=result.question_scores,
            lowest_scoring_areas=result.lowest_scoring_areas,
            highest_scoring_areas=result.highest_scoring_areas
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve WHO-5 results: {str(e)}"
        )


@router.get("/history")
async def get_who5_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's WHO-5 assessment history.
    
    Returns a list of all WHO-5 assessments completed by the current user.
    """
    try:
        # Get WHO-5 template
        template = session.exec(
            select(TestTemplate).where(TestTemplate.key == WHO5Assessment.KEY)
        ).first()
        
        if not template:
            return []
        
        # Get user's attempts
        attempts = session.exec(
            select(TestAttempt)
            .where(TestAttempt.user_id == current_user.id)
            .where(TestAttempt.template_id == template.id)
            .where(TestAttempt.completed == True)
            .order_by(TestAttempt.created_at.desc())
        ).all()
        
        return [
            {
                "id": attempt.id,
                "completed_at": attempt.created_at,
                "score": attempt.score,
                "interpretation": attempt.interpretation
            }
            for attempt in attempts
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve WHO-5 history: {str(e)}"
        )


@router.get("/scoring-guide")
async def get_who5_scoring_guide(
    current_user: User = Depends(get_current_user)
):
    """
    Get WHO-5 scoring guide and interpretation thresholds.
    
    Returns detailed information about how WHO-5 scores are calculated and interpreted.
    """
    return {
        "scoring_method": {
            "description": "Sum all 5 responses (0-5 each) and multiply by 4",
            "formula": "Percentage Score = (Sum of responses) × 4",
            "raw_score_range": "0-25",
            "percentage_range": "0-100%"
        },
        "response_scale": WHO5Assessment.RESPONSE_SCALE,
        "interpretation_levels": {
            "poor": {
                "range": "0-28%",
                "description": "Poor wellbeing - immediate attention recommended",
                "action": "Consider professional support"
            },
            "below_average": {
                "range": "29-50%",
                "description": "Below average wellbeing - support beneficial",
                "action": "Depression screening recommended"
            },
            "average": {
                "range": "51-68%",
                "description": "Average wellbeing - room for improvement",
                "action": "Consider wellbeing strategies"
            },
            "good": {
                "range": "69-84%",
                "description": "Good wellbeing - maintain current practices",
                "action": "Continue positive habits"
            },
            "excellent": {
                "range": "85-100%",
                "description": "Excellent wellbeing - thriving",
                "action": "Share strategies with others"
            }
        },
        "clinical_thresholds": {
            "depression_screening": {
                "threshold": WHO5Assessment.DEPRESSION_SCREENING_THRESHOLD,
                "description": "Scores ≤ 50% suggest depression screening is recommended"
            }
        },
        "question_areas": [
            {"id": 1, "area": "mood", "description": "Cheerful mood and good spirits"},
            {"id": 2, "area": "relaxation", "description": "Feeling calm and relaxed"},
            {"id": 3, "area": "energy", "description": "Active and vigorous energy"},
            {"id": 4, "area": "sleep", "description": "Restorative sleep and rest"},
            {"id": 5, "area": "interest", "description": "Interest in daily activities"}
        ]
    }
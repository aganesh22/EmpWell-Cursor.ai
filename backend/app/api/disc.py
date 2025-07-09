"""
API endpoints for DISC Assessment.

This module provides REST API endpoints for administering and scoring the DISC assessment.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from backend.app.database import get_session
from backend.app.models import TestTemplate, TestAttempt, Response, User
from backend.app.core.disc_assessment import DISCAssessment, DISCResult
from backend.app.deps import get_current_user

router = APIRouter(prefix="/disc", tags=["DISC Assessment"])


class DISCResponseRequest(BaseModel):
    """Request model for DISC assessment responses."""
    most_responses: List[int] = Field(
        ..., 
        description="List of 28 indices (0-3) for words that MOST describe you",
        min_items=28,
        max_items=28
    )
    least_responses: List[int] = Field(
        ..., 
        description="List of 28 indices (0-3) for words that LEAST describe you",
        min_items=28,
        max_items=28
    )


class DISCResultResponse(BaseModel):
    """Response model for DISC assessment results."""
    dimension_scores: Dict[str, float]
    dimension_percentages: Dict[str, float]
    primary_style: str
    secondary_style: str | None
    profile_type: str
    intensity_level: str
    
    # Detailed analysis
    strengths: List[str]
    potential_challenges: List[str]
    communication_style: str
    motivation_factors: List[str]
    stress_indicators: List[str]
    leadership_style: str
    team_contribution: str
    development_areas: List[str]
    
    # Workplace insights
    ideal_environment: List[str]
    decision_making_style: str
    conflict_resolution: str
    change_adaptation: str


class DISCQuestionResponse(BaseModel):
    """Response model for DISC questions."""
    id: int
    instruction: str
    words: List[Dict[str, Any]]
    type: str
    required: bool


@router.get("/questions", response_model=List[DISCQuestionResponse])
async def get_disc_questions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get DISC assessment questions.
    
    Returns all 28 question groups with their word choices for the DISC assessment.
    """
    try:
        questions = DISCAssessment.get_question_data()
        return [DISCQuestionResponse(**q) for q in questions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve DISC questions: {str(e)}"
        )


@router.post("/submit", response_model=DISCResultResponse)
async def submit_disc_assessment(
    request: DISCResponseRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Submit DISC assessment responses and get results.
    
    Processes the user's responses to calculate their DISC profile and returns
    comprehensive analysis including behavioral insights and workplace recommendations.
    """
    try:
        # Validate responses
        is_valid, errors = DISCAssessment.validate_response_set(
            request.most_responses, 
            request.least_responses
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid responses: {'; '.join(errors)}"
            )
        
        # Calculate DISC profile
        result = DISCAssessment.calculate_disc_profile(
            request.most_responses,
            request.least_responses
        )
        
        # Get or create test template
        template = DISCAssessment.create_database_template(session)
        
        # Create test attempt record
        test_attempt = TestAttempt(
            user_id=current_user.id,
            template_id=template.id,
            completed=True,
            score=result.dimension_percentages[result.primary_style],
            interpretation=f"Primary: {result.primary_style.value}, Secondary: {result.secondary_style.value if result.secondary_style else 'None'}"
        )
        session.add(test_attempt)
        session.commit()
        session.refresh(test_attempt)
        
        # Store individual responses
        questions = DISCAssessment.QUESTIONS
        for i, (most_idx, least_idx) in enumerate(zip(request.most_responses, request.least_responses)):
            # Store "most" response
            most_response = Response(
                attempt_id=test_attempt.id,
                question_id=None,  # We'll use question_order since we don't have individual question IDs
                question_order=i + 1,
                value=most_idx,
                response_type="most"
            )
            session.add(most_response)
            
            # Store "least" response
            least_response = Response(
                attempt_id=test_attempt.id,
                question_id=None,
                question_order=i + 1,
                value=least_idx,
                response_type="least"
            )
            session.add(least_response)
        
        session.commit()
        
        # Return formatted result
        return DISCResultResponse(
            dimension_scores={dim.value: score for dim, score in result.dimension_scores.items()},
            dimension_percentages={dim.value: pct for dim, pct in result.dimension_percentages.items()},
            primary_style=result.primary_style.value,
            secondary_style=result.secondary_style.value if result.secondary_style else None,
            profile_type=result.profile_type.value,
            intensity_level=result.intensity_level,
            strengths=result.strengths,
            potential_challenges=result.potential_challenges,
            communication_style=result.communication_style,
            motivation_factors=result.motivation_factors,
            stress_indicators=result.stress_indicators,
            leadership_style=result.leadership_style,
            team_contribution=result.team_contribution,
            development_areas=result.development_areas,
            ideal_environment=result.ideal_environment,
            decision_making_style=result.decision_making_style,
            conflict_resolution=result.conflict_resolution,
            change_adaptation=result.change_adaptation
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process DISC assessment: {str(e)}"
        )


@router.get("/info")
async def get_disc_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get general information about the DISC assessment.
    
    Returns metadata about the assessment including name, description, and administration time.
    """
    return {
        "name": DISCAssessment.NAME,
        "key": DISCAssessment.KEY,
        "version": DISCAssessment.VERSION,
        "administration_time": DISCAssessment.ADMINISTRATION_TIME,
        "description": "DISC is a behavioral assessment tool that measures four primary behavioral dimensions: Dominance, Influence, Steadiness, and Conscientiousness. It helps individuals understand their behavioral preferences and communication styles.",
        "dimensions": {
            "D": "Dominance - How you respond to problems and challenges",
            "I": "Influence - How you influence others to your point of view", 
            "S": "Steadiness - How you respond to the pace of the environment",
            "C": "Conscientiousness - How you respond to rules and procedures"
        },
        "question_count": len(DISCAssessment.QUESTIONS),
        "response_format": "forced_choice",
        "scoring_method": "weighted_selection"
    }


@router.get("/results/{attempt_id}", response_model=DISCResultResponse)
async def get_disc_results(
    attempt_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve previous DISC assessment results.
    
    Returns the results of a previously completed DISC assessment by attempt ID.
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
                detail="DISC assessment attempt not found"
            )
        
        # Get responses
        responses = session.exec(
            select(Response)
            .where(Response.attempt_id == attempt_id)
            .order_by(Response.question_order)
        ).all()
        
        # Separate most and least responses
        most_responses = []
        least_responses = []
        
        for response in responses:
            if response.response_type == "most":
                most_responses.append(response.value)
            elif response.response_type == "least":
                least_responses.append(response.value)
        
        if len(most_responses) != 28 or len(least_responses) != 28:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incomplete response data found"
            )
        
        # Recalculate results
        result = DISCAssessment.calculate_disc_profile(most_responses, least_responses)
        
        return DISCResultResponse(
            dimension_scores={dim.value: score for dim, score in result.dimension_scores.items()},
            dimension_percentages={dim.value: pct for dim, pct in result.dimension_percentages.items()},
            primary_style=result.primary_style.value,
            secondary_style=result.secondary_style.value if result.secondary_style else None,
            profile_type=result.profile_type.value,
            intensity_level=result.intensity_level,
            strengths=result.strengths,
            potential_challenges=result.potential_challenges,
            communication_style=result.communication_style,
            motivation_factors=result.motivation_factors,
            stress_indicators=result.stress_indicators,
            leadership_style=result.leadership_style,
            team_contribution=result.team_contribution,
            development_areas=result.development_areas,
            ideal_environment=result.ideal_environment,
            decision_making_style=result.decision_making_style,
            conflict_resolution=result.conflict_resolution,
            change_adaptation=result.change_adaptation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve DISC results: {str(e)}"
        )


@router.get("/history")
async def get_disc_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's DISC assessment history.
    
    Returns a list of all DISC assessments completed by the current user.
    """
    try:
        # Get DISC template
        template = session.exec(
            select(TestTemplate).where(TestTemplate.key == DISCAssessment.KEY)
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
            detail=f"Failed to retrieve DISC history: {str(e)}"
        )
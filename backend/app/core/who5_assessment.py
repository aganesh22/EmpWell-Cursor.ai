"""
WHO-5 Wellbeing Index Implementation.

This module provides a comprehensive WHO-5 (WHO-Five Well-Being Index) assessment 
that measures current mental wellbeing over the past two weeks.

The WHO-5 is a short questionnaire consisting of 5 simple and non-invasive questions,
which tap into subjective wellbeing. It has been found to have adequate validity both
as a screening tool for depression and as an outcome measure in clinical trials.

Reference: World Health Organization (WHO) - WHO-5 Well-Being Index
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from sqlmodel import Session

from backend.app.models import TestTemplate, Question, TestAttempt, Response


class WHO5ScoreLevel(str, Enum):
    """WHO-5 score interpretation levels."""
    POOR = "poor"
    BELOW_AVERAGE = "below_average"
    AVERAGE = "average"
    GOOD = "good"
    EXCELLENT = "excellent"


@dataclass
class WHO5Result:
    """Result of WHO-5 assessment."""
    raw_score: int  # Sum of all responses (0-25)
    percentage_score: int  # Raw score * 4 (0-100)
    score_level: WHO5ScoreLevel
    
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


class WHO5Assessment:
    """
    WHO-5 Wellbeing Index Implementation.
    
    The WHO-5 is a 5-item questionnaire that measures current mental wellbeing
    over the past two weeks. Each item is rated on a 6-point Likert scale
    from 0 (not present) to 5 (constantly present).
    """
    
    NAME = "WHO-5 Well-Being Index"
    KEY = "who5"
    VERSION = "1.0"
    ADMINISTRATION_TIME = "2-3 minutes"
    
    # WHO-5 Questions - Standard validated questions
    QUESTIONS = [
        {
            "id": 1,
            "text": "I have felt cheerful and in good spirits",
            "timeframe": "Over the last two weeks",
            "area": "mood"
        },
        {
            "id": 2,
            "text": "I have felt calm and relaxed",
            "timeframe": "Over the last two weeks",
            "area": "relaxation"
        },
        {
            "id": 3,
            "text": "I have felt active and vigorous",
            "timeframe": "Over the last two weeks",
            "area": "energy"
        },
        {
            "id": 4,
            "text": "I woke up feeling fresh and rested",
            "timeframe": "Over the last two weeks",
            "area": "sleep"
        },
        {
            "id": 5,
            "text": "My daily life has been filled with things that interest me",
            "timeframe": "Over the last two weeks",
            "area": "interest"
        }
    ]
    
    # Response scale
    RESPONSE_SCALE = [
        {"value": 0, "label": "At no time", "description": "Not present at all"},
        {"value": 1, "label": "Some of the time", "description": "Occasionally present"},
        {"value": 2, "label": "Less than half of the time", "description": "Present but not frequent"},
        {"value": 3, "label": "More than half of the time", "description": "Frequently present"},
        {"value": 4, "label": "Most of the time", "description": "Almost always present"},
        {"value": 5, "label": "All of the time", "description": "Constantly present"}
    ]
    
    # Score interpretation thresholds
    SCORE_THRESHOLDS = {
        WHO5ScoreLevel.POOR: (0, 28),           # 0-28%: Poor wellbeing
        WHO5ScoreLevel.BELOW_AVERAGE: (29, 50), # 29-50%: Below average
        WHO5ScoreLevel.AVERAGE: (51, 68),       # 51-68%: Average
        WHO5ScoreLevel.GOOD: (69, 84),          # 69-84%: Good
        WHO5ScoreLevel.EXCELLENT: (85, 100)     # 85-100%: Excellent
    }
    
    # Depression screening threshold (WHO-5 score ≤ 50 suggests depression screening)
    DEPRESSION_SCREENING_THRESHOLD = 50
    
    @classmethod
    def calculate_who5_score(cls, responses: List[int]) -> WHO5Result:
        """
        Calculate WHO-5 score from responses.
        
        Args:
            responses: List of 5 integers (0-5) representing responses to each question
            
        Returns:
            WHO5Result with complete analysis
        """
        if len(responses) != 5:
            raise ValueError("WHO-5 assessment requires exactly 5 responses")
        
        if not all(isinstance(r, int) and 0 <= r <= 5 for r in responses):
            raise ValueError("All responses must be integers between 0 and 5")
        
        # Calculate raw score (sum of all responses)
        raw_score = sum(responses)
        
        # Calculate percentage score (raw score * 4)
        percentage_score = raw_score * 4
        
        # Determine score level
        score_level = cls._get_score_level(percentage_score)
        
        # Generate interpretation
        interpretation = cls._get_interpretation(percentage_score, score_level)
        
        # Generate recommendations
        recommendations = cls._get_recommendations(percentage_score, responses)
        
        # Identify risk indicators
        risk_indicators = cls._get_risk_indicators(percentage_score, responses)
        
        # Identify strengths
        strengths = cls._get_strengths(responses)
        
        # Clinical insights
        depression_screening = cls._get_depression_screening(percentage_score)
        wellbeing_status = cls._get_wellbeing_status(percentage_score)
        follow_up_needed = percentage_score <= cls.DEPRESSION_SCREENING_THRESHOLD
        
        # Question analysis
        question_scores = {i + 1: score for i, score in enumerate(responses)}
        lowest_scoring_areas = cls._get_lowest_scoring_areas(responses)
        highest_scoring_areas = cls._get_highest_scoring_areas(responses)
        
        return WHO5Result(
            raw_score=raw_score,
            percentage_score=percentage_score,
            score_level=score_level,
            interpretation=interpretation,
            recommendations=recommendations,
            risk_indicators=risk_indicators,
            strengths=strengths,
            depression_screening=depression_screening,
            wellbeing_status=wellbeing_status,
            follow_up_needed=follow_up_needed,
            question_scores=question_scores,
            lowest_scoring_areas=lowest_scoring_areas,
            highest_scoring_areas=highest_scoring_areas
        )
    
    @classmethod
    def _get_score_level(cls, percentage_score: int) -> WHO5ScoreLevel:
        """Get score level based on percentage score."""
        for level, (min_score, max_score) in cls.SCORE_THRESHOLDS.items():
            if min_score <= percentage_score <= max_score:
                return level
        return WHO5ScoreLevel.POOR  # Default fallback
    
    @classmethod
    def _get_interpretation(cls, percentage_score: int, score_level: WHO5ScoreLevel) -> str:
        """Get detailed interpretation based on score."""
        interpretations = {
            WHO5ScoreLevel.POOR: f"Your WHO-5 score of {percentage_score}% indicates poor wellbeing. This suggests you may be experiencing significant challenges with your mental health and overall life satisfaction. It's important to seek support and consider professional help.",
            
            WHO5ScoreLevel.BELOW_AVERAGE: f"Your WHO-5 score of {percentage_score}% indicates below-average wellbeing. While not critically low, this suggests there's room for improvement in your mental health and life satisfaction. Consider implementing wellbeing strategies or seeking support.",
            
            WHO5ScoreLevel.AVERAGE: f"Your WHO-5 score of {percentage_score}% indicates average wellbeing. You're experiencing a moderate level of mental health and life satisfaction, which is typical for many people. There are still opportunities to enhance your wellbeing further.",
            
            WHO5ScoreLevel.GOOD: f"Your WHO-5 score of {percentage_score}% indicates good wellbeing. You're experiencing positive mental health and life satisfaction most of the time. Continue with the practices that support your wellbeing.",
            
            WHO5ScoreLevel.EXCELLENT: f"Your WHO-5 score of {percentage_score}% indicates excellent wellbeing. You're experiencing high levels of mental health and life satisfaction. You're doing well in maintaining your psychological wellbeing."
        }
        
        return interpretations.get(score_level, "Score interpretation not available.")
    
    @classmethod
    def _get_recommendations(cls, percentage_score: int, responses: List[int]) -> List[str]:
        """Get personalized recommendations based on score and responses."""
        recommendations = []
        
        # General recommendations based on score level
        if percentage_score <= 28:
            recommendations.extend([
                "Consider speaking with a mental health professional",
                "Reach out to trusted friends, family, or support services",
                "Focus on basic self-care: regular sleep, nutrition, and gentle exercise",
                "Consider mindfulness or relaxation techniques",
                "Avoid major life decisions until wellbeing improves"
            ])
        elif percentage_score <= 50:
            recommendations.extend([
                "Consider professional support or counseling",
                "Implement stress management techniques",
                "Focus on activities that bring you joy and satisfaction",
                "Maintain regular sleep and exercise routines",
                "Connect with supportive people in your life"
            ])
        elif percentage_score <= 68:
            recommendations.extend([
                "Continue current positive practices",
                "Consider adding new wellbeing activities to your routine",
                "Focus on work-life balance",
                "Engage in regular physical activity",
                "Practice gratitude and mindfulness"
            ])
        else:
            recommendations.extend([
                "Maintain your current wellbeing practices",
                "Consider sharing your strategies with others",
                "Continue regular self-care routines",
                "Stay connected with your support network",
                "Monitor your wellbeing regularly"
            ])
        
        # Specific recommendations based on individual responses
        question_areas = ["mood", "relaxation", "energy", "sleep", "interest"]
        
        for i, (response, area) in enumerate(zip(responses, question_areas)):
            if response <= 2:  # Low scores need specific attention
                if area == "mood":
                    recommendations.append("Try mood-boosting activities like socializing or hobbies")
                elif area == "relaxation":
                    recommendations.append("Practice relaxation techniques like deep breathing or meditation")
                elif area == "energy":
                    recommendations.append("Focus on regular exercise and balanced nutrition")
                elif area == "sleep":
                    recommendations.append("Improve sleep hygiene and consider a consistent bedtime routine")
                elif area == "interest":
                    recommendations.append("Explore new activities or reconnect with past interests")
        
        return list(set(recommendations))  # Remove duplicates
    
    @classmethod
    def _get_risk_indicators(cls, percentage_score: int, responses: List[int]) -> List[str]:
        """Identify risk indicators based on score and responses."""
        risk_indicators = []
        
        # Overall risk based on score
        if percentage_score <= cls.DEPRESSION_SCREENING_THRESHOLD:
            risk_indicators.append("Score suggests potential depression screening needed")
        
        if percentage_score <= 28:
            risk_indicators.append("Very low wellbeing indicates high risk for mental health concerns")
        
        # Specific risk indicators based on individual responses
        question_areas = ["mood", "relaxation", "energy", "sleep", "interest"]
        
        for i, (response, area) in enumerate(zip(responses, question_areas)):
            if response == 0:  # Score of 0 is particularly concerning
                if area == "mood":
                    risk_indicators.append("Complete absence of positive mood")
                elif area == "relaxation":
                    risk_indicators.append("Inability to feel calm or relaxed")
                elif area == "energy":
                    risk_indicators.append("Complete lack of energy and vigor")
                elif area == "sleep":
                    risk_indicators.append("Persistent sleep problems")
                elif area == "interest":
                    risk_indicators.append("Complete loss of interest in daily activities")
        
        # Check for multiple low scores
        low_scores = sum(1 for r in responses if r <= 1)
        if low_scores >= 3:
            risk_indicators.append("Multiple areas of very low wellbeing")
        
        return risk_indicators
    
    @classmethod
    def _get_strengths(cls, responses: List[int]) -> List[str]:
        """Identify strengths based on responses."""
        strengths = []
        question_areas = ["mood", "relaxation", "energy", "sleep", "interest"]
        
        for i, (response, area) in enumerate(zip(responses, question_areas)):
            if response >= 4:  # High scores indicate strengths
                if area == "mood":
                    strengths.append("Maintains positive mood and good spirits")
                elif area == "relaxation":
                    strengths.append("Able to feel calm and relaxed")
                elif area == "energy":
                    strengths.append("Maintains good energy levels and vitality")
                elif area == "sleep":
                    strengths.append("Gets restorative sleep and wakes refreshed")
                elif area == "interest":
                    strengths.append("Finds life interesting and engaging")
        
        if not strengths:
            # Find the highest scoring area even if it's not high
            max_score = max(responses)
            if max_score >= 2:
                max_index = responses.index(max_score)
                area = question_areas[max_index]
                strengths.append(f"Relatively stronger in {area} compared to other areas")
        
        return strengths
    
    @classmethod
    def _get_depression_screening(cls, percentage_score: int) -> str:
        """Get depression screening recommendation."""
        if percentage_score <= cls.DEPRESSION_SCREENING_THRESHOLD:
            return "Score suggests depression screening is recommended. Consider consulting with a healthcare professional for further evaluation."
        else:
            return "Score does not indicate immediate need for depression screening, but regular monitoring is beneficial."
    
    @classmethod
    def _get_wellbeing_status(cls, percentage_score: int) -> str:
        """Get overall wellbeing status."""
        if percentage_score <= 28:
            return "Poor wellbeing - immediate attention recommended"
        elif percentage_score <= 50:
            return "Below average wellbeing - support and intervention beneficial"
        elif percentage_score <= 68:
            return "Average wellbeing - room for improvement"
        elif percentage_score <= 84:
            return "Good wellbeing - maintain current practices"
        else:
            return "Excellent wellbeing - thriving mentally and emotionally"
    
    @classmethod
    def _get_lowest_scoring_areas(cls, responses: List[int]) -> List[str]:
        """Identify areas with lowest scores."""
        question_areas = ["mood", "relaxation", "energy", "sleep", "interest"]
        min_score = min(responses)
        
        lowest_areas = []
        for i, (response, area) in enumerate(zip(responses, question_areas)):
            if response == min_score:
                area_descriptions = {
                    "mood": "Cheerful mood and good spirits",
                    "relaxation": "Feeling calm and relaxed",
                    "energy": "Active and vigorous energy",
                    "sleep": "Restorative sleep and rest",
                    "interest": "Interest in daily activities"
                }
                lowest_areas.append(area_descriptions[area])
        
        return lowest_areas
    
    @classmethod
    def _get_highest_scoring_areas(cls, responses: List[int]) -> List[str]:
        """Identify areas with highest scores."""
        question_areas = ["mood", "relaxation", "energy", "sleep", "interest"]
        max_score = max(responses)
        
        highest_areas = []
        for i, (response, area) in enumerate(zip(responses, question_areas)):
            if response == max_score and response >= 3:  # Only consider genuinely high scores
                area_descriptions = {
                    "mood": "Cheerful mood and good spirits",
                    "relaxation": "Feeling calm and relaxed",
                    "energy": "Active and vigorous energy",
                    "sleep": "Restorative sleep and rest",
                    "interest": "Interest in daily activities"
                }
                highest_areas.append(area_descriptions[area])
        
        return highest_areas
    
    @classmethod
    def get_question_data(cls) -> List[Dict[str, Any]]:
        """Get question data for frontend display."""
        return [
            {
                "id": question["id"],
                "text": question["text"],
                "timeframe": question["timeframe"],
                "area": question["area"],
                "response_scale": cls.RESPONSE_SCALE,
                "type": "likert",
                "required": True,
                "min_value": 0,
                "max_value": 5
            }
            for question in cls.QUESTIONS
        ]
    
    @classmethod
    def validate_responses(cls, responses: List[int]) -> Tuple[bool, List[str]]:
        """Validate WHO-5 responses."""
        errors = []
        
        if len(responses) != 5:
            errors.append(f"Expected 5 responses, got {len(responses)}")
        
        for i, response in enumerate(responses):
            if not isinstance(response, int):
                errors.append(f"Question {i+1}: Response must be an integer")
                continue
            
            if not (0 <= response <= 5):
                errors.append(f"Question {i+1}: Response must be between 0 and 5")
        
        return len(errors) == 0, errors
    
    @classmethod
    def create_database_template(cls, session: Session) -> TestTemplate:
        """Create WHO-5 assessment template in the database."""
        from sqlmodel import select
        
        # Check if template already exists
        existing = session.exec(
            select(TestTemplate).where(TestTemplate.key == cls.KEY)
        ).first()
        
        if existing:
            return existing
        
        # Create template
        template = TestTemplate(
            key=cls.KEY,
            name=cls.NAME,
            description=f"WHO-5 Well-Being Index - {cls.ADMINISTRATION_TIME}"
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        # Create questions
        for question_data in cls.QUESTIONS:
            question = Question(
                template_id=template.id,
                text=question_data["text"],
                order=question_data["id"],
                min_value=0,
                max_value=5,
                weight=1.0,
                dimension_pair=question_data["area"],
                positive_letter=None,
                show_if_question_id=None,
                show_if_value=None
            )
            session.add(question)
        
        session.commit()
        return template


# Convenience function
def calculate_who5_score(responses: List[int]) -> WHO5Result:
    """Convenience function to calculate WHO-5 score."""
    return WHO5Assessment.calculate_who5_score(responses)
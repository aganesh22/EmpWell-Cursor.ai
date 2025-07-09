"""
DISC Assessment Implementation.

This module provides a comprehensive DISC personality assessment that measures four behavioral dimensions:
- Dominance (D): How you respond to problems and challenges
- Influence (I): How you influence others to your point of view
- Steadiness (S): How you respond to the pace of the environment
- Conscientiousness (C): How you respond to rules and procedures

The DISC assessment is widely used in workplace settings for team building, leadership development,
and communication improvement.

Reference: William Moulton Marston's DISC theory and modern adaptations.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import statistics
from sqlmodel import Session

from backend.app.models import TestTemplate, Question, TestAttempt, Response


class DISCDimension(str, Enum):
    """The four DISC dimensions."""
    DOMINANCE = "D"
    INFLUENCE = "I"
    STEADINESS = "S"
    CONSCIENTIOUSNESS = "C"


class DISCProfile(str, Enum):
    """Common DISC profile combinations."""
    # Primary styles (single dimension dominant)
    DOMINANT = "D"
    INFLUENTIAL = "I"
    STEADY = "S"
    CONSCIENTIOUS = "C"
    
    # Combination styles (two dimensions)
    DOMINANCE_INFLUENCE = "DI"
    DOMINANCE_STEADINESS = "DS"
    DOMINANCE_CONSCIENTIOUSNESS = "DC"
    INFLUENCE_DOMINANCE = "ID"
    INFLUENCE_STEADINESS = "IS"
    INFLUENCE_CONSCIENTIOUSNESS = "IC"
    STEADINESS_DOMINANCE = "SD"
    STEADINESS_INFLUENCE = "SI"
    STEADINESS_CONSCIENTIOUSNESS = "SC"
    CONSCIENTIOUSNESS_DOMINANCE = "CD"
    CONSCIENTIOUSNESS_INFLUENCE = "CI"
    CONSCIENTIOUSNESS_STEADINESS = "CS"


@dataclass
class DISCResult:
    """Result of DISC assessment."""
    dimension_scores: Dict[DISCDimension, float]
    dimension_percentages: Dict[DISCDimension, float]
    primary_style: DISCDimension
    secondary_style: Optional[DISCDimension]
    profile_type: DISCProfile
    intensity_level: str  # High, Moderate, Low
    
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


class DISCAssessment:
    """
    DISC Assessment Implementation.
    
    This assessment measures four behavioral dimensions through forced-choice questions
    where participants select words that most and least describe them.
    """
    
    NAME = "DISC Behavioral Assessment"
    KEY = "disc"
    VERSION = "1.0"
    ADMINISTRATION_TIME = "8-12 minutes"
    
    # DISC Question Bank - 28 question groups with 4 words each
    QUESTIONS = [
        {
            "id": 1,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Adventurous", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Adaptable", "dimension": DISCDimension.INFLUENCE, "weight": 1.0},
                {"text": "Animated", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Analytical", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0}
            ]
        },
        {
            "id": 2,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Persistent", "dimension": DISCDimension.DOMINANCE, "weight": 0.8},
                {"text": "Playful", "dimension": DISCDimension.INFLUENCE, "weight": 1.0},
                {"text": "Persuasive", "dimension": DISCDimension.INFLUENCE, "weight": 0.9},
                {"text": "Peaceful", "dimension": DISCDimension.STEADINESS, "weight": 1.0}
            ]
        },
        {
            "id": 3,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Submissive", "dimension": DISCDimension.STEADINESS, "weight": 0.7},
                {"text": "Self-reliant", "dimension": DISCDimension.DOMINANCE, "weight": 0.9},
                {"text": "Sociable", "dimension": DISCDimension.INFLUENCE, "weight": 1.0},
                {"text": "Strong-willed", "dimension": DISCDimension.DOMINANCE, "weight": 1.0}
            ]
        },
        {
            "id": 4,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Considerate", "dimension": DISCDimension.STEADINESS, "weight": 1.0},
                {"text": "Controlled", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.8},
                {"text": "Competitive", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Convincing", "dimension": DISCDimension.INFLUENCE, "weight": 0.9}
            ]
        },
        {
            "id": 5,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Refreshing", "dimension": DISCDimension.INFLUENCE, "weight": 0.7},
                {"text": "Respectful", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Reserved", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.9},
                {"text": "Resourceful", "dimension": DISCDimension.DOMINANCE, "weight": 0.8}
            ]
        },
        {
            "id": 6,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Satisfied", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Sensitive", "dimension": DISCDimension.STEADINESS, "weight": 0.9},
                {"text": "Self-assured", "dimension": DISCDimension.DOMINANCE, "weight": 0.9},
                {"text": "Spirited", "dimension": DISCDimension.INFLUENCE, "weight": 1.0}
            ]
        },
        {
            "id": 7,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Planner", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0},
                {"text": "Patient", "dimension": DISCDimension.STEADINESS, "weight": 1.0},
                {"text": "Positive", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Pioneering", "dimension": DISCDimension.DOMINANCE, "weight": 0.9}
            ]
        },
        {
            "id": 8,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Sure", "dimension": DISCDimension.DOMINANCE, "weight": 0.7},
                {"text": "Spontaneous", "dimension": DISCDimension.INFLUENCE, "weight": 0.9},
                {"text": "Scheduled", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.8},
                {"text": "Shy", "dimension": DISCDimension.STEADINESS, "weight": 0.6}
            ]
        },
        {
            "id": 9,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Orderly", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0},
                {"text": "Obliging", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Outspoken", "dimension": DISCDimension.DOMINANCE, "weight": 0.9},
                {"text": "Optimistic", "dimension": DISCDimension.INFLUENCE, "weight": 1.0}
            ]
        },
        {
            "id": 10,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Friendly", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Forceful", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Faithful", "dimension": DISCDimension.STEADINESS, "weight": 0.9},
                {"text": "Factual", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0}
            ]
        },
        {
            "id": 11,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Accurate", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0},
                {"text": "Adventurous", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Agreeable", "dimension": DISCDimension.STEADINESS, "weight": 0.9},
                {"text": "Attractive", "dimension": DISCDimension.INFLUENCE, "weight": 0.7}
            ]
        },
        {
            "id": 12,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Demanding", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Demonstrative", "dimension": DISCDimension.INFLUENCE, "weight": 0.9},
                {"text": "Dependable", "dimension": DISCDimension.STEADINESS, "weight": 1.0},
                {"text": "Detailed", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.9}
            ]
        },
        {
            "id": 13,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Enthusiastic", "dimension": DISCDimension.INFLUENCE, "weight": 1.0},
                {"text": "Energetic", "dimension": DISCDimension.DOMINANCE, "weight": 0.8},
                {"text": "Even-tempered", "dimension": DISCDimension.STEADINESS, "weight": 0.9},
                {"text": "Exacting", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.8}
            ]
        },
        {
            "id": 14,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Bold", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Balanced", "dimension": DISCDimension.STEADINESS, "weight": 0.7},
                {"text": "Buoyant", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Businesslike", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.9}
            ]
        },
        {
            "id": 15,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Decisive", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Delightful", "dimension": DISCDimension.INFLUENCE, "weight": 0.7},
                {"text": "Diplomatic", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Disciplined", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0}
            ]
        },
        {
            "id": 16,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Confident", "dimension": DISCDimension.DOMINANCE, "weight": 0.9},
                {"text": "Charming", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Consistent", "dimension": DISCDimension.STEADINESS, "weight": 1.0},
                {"text": "Cautious", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.9}
            ]
        },
        {
            "id": 17,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Restless", "dimension": DISCDimension.DOMINANCE, "weight": 0.7},
                {"text": "Responsive", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Relaxed", "dimension": DISCDimension.STEADINESS, "weight": 0.9},
                {"text": "Refined", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.8}
            ]
        },
        {
            "id": 18,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Willing", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Winsome", "dimension": DISCDimension.INFLUENCE, "weight": 0.7},
                {"text": "Workaholic", "dimension": DISCDimension.DOMINANCE, "weight": 0.6},
                {"text": "Withdrawn", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.7}
            ]
        },
        {
            "id": 19,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Argumentative", "dimension": DISCDimension.DOMINANCE, "weight": 0.8},
                {"text": "Animated", "dimension": DISCDimension.INFLUENCE, "weight": 0.9},
                {"text": "Amiable", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Avoids risks", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.7}
            ]
        },
        {
            "id": 20,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Impatient", "dimension": DISCDimension.DOMINANCE, "weight": 0.7},
                {"text": "Impulsive", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Indecisive", "dimension": DISCDimension.STEADINESS, "weight": 0.6},
                {"text": "Inflexible", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.7}
            ]
        },
        {
            "id": 21,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Daring", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Delightful", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Dependable", "dimension": DISCDimension.STEADINESS, "weight": 1.0},
                {"text": "Detailed", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.9}
            ]
        },
        {
            "id": 22,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Inspiring", "dimension": DISCDimension.INFLUENCE, "weight": 1.0},
                {"text": "Independent", "dimension": DISCDimension.DOMINANCE, "weight": 0.9},
                {"text": "Inoffensive", "dimension": DISCDimension.STEADINESS, "weight": 0.7},
                {"text": "Introspective", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.8}
            ]
        },
        {
            "id": 23,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Jovial", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Joyful", "dimension": DISCDimension.INFLUENCE, "weight": 0.9},
                {"text": "Just", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.8},
                {"text": "Jumpy", "dimension": DISCDimension.DOMINANCE, "weight": 0.6}
            ]
        },
        {
            "id": 24,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Logical", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0},
                {"text": "Loyal", "dimension": DISCDimension.STEADINESS, "weight": 1.0},
                {"text": "Lively", "dimension": DISCDimension.INFLUENCE, "weight": 0.9},
                {"text": "Leader", "dimension": DISCDimension.DOMINANCE, "weight": 1.0}
            ]
        },
        {
            "id": 25,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Mover", "dimension": DISCDimension.DOMINANCE, "weight": 0.8},
                {"text": "Mixer", "dimension": DISCDimension.INFLUENCE, "weight": 0.9},
                {"text": "Modest", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Meticulous", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0}
            ]
        },
        {
            "id": 26,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Tenacious", "dimension": DISCDimension.DOMINANCE, "weight": 0.9},
                {"text": "Talkative", "dimension": DISCDimension.INFLUENCE, "weight": 1.0},
                {"text": "Tolerant", "dimension": DISCDimension.STEADINESS, "weight": 0.9},
                {"text": "Thorough", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 1.0}
            ]
        },
        {
            "id": 27,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Listener", "dimension": DISCDimension.STEADINESS, "weight": 0.9},
                {"text": "Loyal", "dimension": DISCDimension.STEADINESS, "weight": 1.0},
                {"text": "Leader", "dimension": DISCDimension.DOMINANCE, "weight": 1.0},
                {"text": "Lively", "dimension": DISCDimension.INFLUENCE, "weight": 0.9}
            ]
        },
        {
            "id": 28,
            "instruction": "Select the word that MOST describes you and the word that LEAST describes you:",
            "words": [
                {"text": "Contented", "dimension": DISCDimension.STEADINESS, "weight": 0.8},
                {"text": "Chief", "dimension": DISCDimension.DOMINANCE, "weight": 0.9},
                {"text": "Cheerful", "dimension": DISCDimension.INFLUENCE, "weight": 0.8},
                {"text": "Careful", "dimension": DISCDimension.CONSCIENTIOUSNESS, "weight": 0.9}
            ]
        }
    ]
    
    # DISC Style Descriptions
    STYLE_DESCRIPTIONS = {
        DISCDimension.DOMINANCE: {
            "name": "Dominance",
            "description": "Direct, results-oriented, firm, strong-willed, and forceful",
            "core_motivation": "Achieving results and maintaining control",
            "fears": "Being taken advantage of or losing control",
            "strengths": [
                "Results-oriented and goal-focused",
                "Makes quick decisions",
                "Takes charge in crisis situations",
                "Challenges the status quo",
                "Accepts responsibility readily",
                "Drives for bottom-line results"
            ],
            "challenges": [
                "May be impatient with others",
                "Can be overly direct or blunt",
                "May overlook people's feelings",
                "Tendency to be controlling",
                "May make hasty decisions",
                "Can be insensitive to team dynamics"
            ],
            "communication_style": "Direct, brief, and to the point",
            "motivation_factors": [
                "Authority and control",
                "Varied activities and challenges",
                "Opportunities for advancement",
                "Freedom from routine and mundane tasks",
                "Recognition for achievements"
            ],
            "stress_indicators": [
                "Becomes more aggressive",
                "Increases pace and pressure",
                "Becomes impatient with details",
                "May become overly critical"
            ],
            "leadership_style": "Authoritative and decisive",
            "ideal_environment": [
                "Results-oriented atmosphere",
                "Freedom to make decisions",
                "Challenging and varied tasks",
                "Opportunities for advancement",
                "Minimal routine work"
            ]
        },
        DISCDimension.INFLUENCE: {
            "name": "Influence",
            "description": "Outgoing, enthusiastic, optimistic, high-spirited, and lively",
            "core_motivation": "Social recognition and approval from others",
            "fears": "Social rejection or loss of influence",
            "strengths": [
                "Enthusiastic and optimistic",
                "Excellent communicator",
                "Builds relationships easily",
                "Motivates and inspires others",
                "Creative and innovative",
                "Adapts well to change"
            ],
            "challenges": [
                "May be overly talkative",
                "Can be disorganized",
                "May avoid difficult conversations",
                "Tendency to be impulsive",
                "May lack attention to detail",
                "Can be overly optimistic"
            ],
            "communication_style": "Enthusiastic, expressive, and people-focused",
            "motivation_factors": [
                "Social interaction and teamwork",
                "Public recognition and praise",
                "Freedom from routine details",
                "Opportunities to help others",
                "Variety and new experiences"
            ],
            "stress_indicators": [
                "Becomes more talkative",
                "Seeks more social interaction",
                "May become disorganized",
                "Avoids confrontation"
            ],
            "leadership_style": "Inspirational and collaborative",
            "ideal_environment": [
                "People-oriented atmosphere",
                "Opportunities for social interaction",
                "Recognition and praise",
                "Variety and flexibility",
                "Minimal routine work"
            ]
        },
        DISCDimension.STEADINESS: {
            "name": "Steadiness",
            "description": "Even-tempered, accommodating, patient, humble, and tactful",
            "core_motivation": "Maintaining stability and harmony",
            "fears": "Loss of security or sudden change",
            "strengths": [
                "Calm and patient",
                "Excellent team player",
                "Reliable and dependable",
                "Good listener",
                "Supportive of others",
                "Maintains stability"
            ],
            "challenges": [
                "May resist change",
                "Can be overly accommodating",
                "May avoid conflict",
                "Tendency to be indecisive",
                "May lack assertiveness",
                "Can be overly modest"
            ],
            "communication_style": "Calm, supportive, and patient",
            "motivation_factors": [
                "Job security and stability",
                "Appreciation for contributions",
                "Opportunities to help others",
                "Predictable work environment",
                "Team collaboration"
            ],
            "stress_indicators": [
                "Becomes more withdrawn",
                "Increases resistance to change",
                "May become indecisive",
                "Seeks more security"
            ],
            "leadership_style": "Supportive and collaborative",
            "ideal_environment": [
                "Stable and predictable atmosphere",
                "Opportunities for teamwork",
                "Appreciation and recognition",
                "Minimal conflict",
                "Clear expectations"
            ]
        },
        DISCDimension.CONSCIENTIOUSNESS: {
            "name": "Conscientiousness",
            "description": "Careful, cautious, accurate, tactful, and diplomatic",
            "core_motivation": "Accuracy and quality in work",
            "fears": "Criticism of their work or making mistakes",
            "strengths": [
                "High quality standards",
                "Analytical and systematic",
                "Accurate and precise",
                "Diplomatic and tactful",
                "Follows procedures",
                "Thinks before acting"
            ],
            "challenges": [
                "May be overly critical",
                "Can be perfectionist",
                "May avoid taking risks",
                "Tendency to be pessimistic",
                "May be slow to make decisions",
                "Can be overly sensitive to criticism"
            ],
            "communication_style": "Precise, diplomatic, and fact-based",
            "motivation_factors": [
                "Quality standards and accuracy",
                "Detailed information and data",
                "Time to analyze and plan",
                "Opportunities for expertise",
                "Clear expectations and procedures"
            ],
            "stress_indicators": [
                "Becomes more critical",
                "Increases attention to detail",
                "May become paralyzed by analysis",
                "Avoids taking risks"
            ],
            "leadership_style": "Analytical and methodical",
            "ideal_environment": [
                "Quality-focused atmosphere",
                "Clear procedures and standards",
                "Time for analysis and planning",
                "Opportunities for expertise",
                "Minimal pressure for quick decisions"
            ]
        }
    }
    
    @classmethod
    def calculate_disc_profile(cls, most_responses: List[int], least_responses: List[int]) -> DISCResult:
        """
        Calculate DISC profile from most and least responses.
        
        Args:
            most_responses: List of indices (0-3) for words that MOST describe the person
            least_responses: List of indices (0-3) for words that LEAST describe the person
            
        Returns:
            DISCResult with complete profile analysis
        """
        if len(most_responses) != 28 or len(least_responses) != 28:
            raise ValueError("DISC assessment requires exactly 28 most and 28 least responses")
        
        if not all(0 <= r <= 3 for r in most_responses + least_responses):
            raise ValueError("All responses must be between 0 and 3")
        
        # Initialize dimension scores
        dimension_scores = {dim: 0.0 for dim in DISCDimension}
        
        # Calculate scores based on most and least selections
        for i, (most_idx, least_idx) in enumerate(zip(most_responses, least_responses)):
            question = cls.QUESTIONS[i]
            
            # Add points for "most" selection
            most_word = question["words"][most_idx]
            dimension_scores[most_word["dimension"]] += most_word["weight"]
            
            # Subtract points for "least" selection
            least_word = question["words"][least_idx]
            dimension_scores[least_word["dimension"]] -= least_word["weight"] * 0.5
        
        # Convert to percentages
        total_score = sum(abs(score) for score in dimension_scores.values())
        if total_score == 0:
            dimension_percentages = {dim: 25.0 for dim in DISCDimension}
        else:
            dimension_percentages = {
                dim: max(0, (score / total_score) * 100) 
                for dim, score in dimension_scores.items()
            }
        
        # Determine primary and secondary styles
        sorted_dimensions = sorted(
            dimension_percentages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        primary_style = sorted_dimensions[0][0]
        secondary_style = sorted_dimensions[1][0] if sorted_dimensions[1][1] > 20 else None
        
        # Determine profile type
        if secondary_style and sorted_dimensions[1][1] > 25:
            profile_type = DISCProfile(primary_style.value + secondary_style.value)
        else:
            profile_type = DISCProfile(primary_style.value)
        
        # Determine intensity level
        primary_percentage = sorted_dimensions[0][1]
        if primary_percentage > 40:
            intensity_level = "High"
        elif primary_percentage > 30:
            intensity_level = "Moderate"
        else:
            intensity_level = "Low"
        
        # Get detailed analysis
        primary_desc = cls.STYLE_DESCRIPTIONS[primary_style]
        secondary_desc = cls.STYLE_DESCRIPTIONS[secondary_style] if secondary_style else None
        
        # Generate comprehensive profile
        strengths = primary_desc["strengths"].copy()
        if secondary_desc:
            strengths.extend(secondary_desc["strengths"][:3])
        
        challenges = primary_desc["challenges"].copy()
        if secondary_desc:
            challenges.extend(secondary_desc["challenges"][:2])
        
        # Generate workplace insights
        decision_making_style = cls._get_decision_making_style(primary_style, secondary_style)
        conflict_resolution = cls._get_conflict_resolution_style(primary_style, secondary_style)
        change_adaptation = cls._get_change_adaptation_style(primary_style, secondary_style)
        
        return DISCResult(
            dimension_scores=dimension_scores,
            dimension_percentages=dimension_percentages,
            primary_style=primary_style,
            secondary_style=secondary_style,
            profile_type=profile_type,
            intensity_level=intensity_level,
            strengths=strengths[:8],  # Limit to top 8
            potential_challenges=challenges[:6],  # Limit to top 6
            communication_style=primary_desc["communication_style"],
            motivation_factors=primary_desc["motivation_factors"],
            stress_indicators=primary_desc["stress_indicators"],
            leadership_style=primary_desc["leadership_style"],
            team_contribution=cls._get_team_contribution(primary_style, secondary_style),
            development_areas=cls._get_development_areas(primary_style, secondary_style),
            ideal_environment=primary_desc["ideal_environment"],
            decision_making_style=decision_making_style,
            conflict_resolution=conflict_resolution,
            change_adaptation=change_adaptation
        )
    
    @classmethod
    def _get_decision_making_style(cls, primary: DISCDimension, secondary: Optional[DISCDimension]) -> str:
        """Get decision-making style based on DISC profile."""
        if primary == DISCDimension.DOMINANCE:
            return "Quick, decisive, and results-focused"
        elif primary == DISCDimension.INFLUENCE:
            return "Collaborative, people-focused, and optimistic"
        elif primary == DISCDimension.STEADINESS:
            return "Careful, consensus-seeking, and stable"
        else:  # CONSCIENTIOUSNESS
            return "Analytical, data-driven, and methodical"
    
    @classmethod
    def _get_conflict_resolution_style(cls, primary: DISCDimension, secondary: Optional[DISCDimension]) -> str:
        """Get conflict resolution style based on DISC profile."""
        if primary == DISCDimension.DOMINANCE:
            return "Direct confrontation and quick resolution"
        elif primary == DISCDimension.INFLUENCE:
            return "Diplomatic discussion and relationship preservation"
        elif primary == DISCDimension.STEADINESS:
            return "Avoidance initially, then patient mediation"
        else:  # CONSCIENTIOUSNESS
            return "Systematic analysis and fact-based resolution"
    
    @classmethod
    def _get_change_adaptation_style(cls, primary: DISCDimension, secondary: Optional[DISCDimension]) -> str:
        """Get change adaptation style based on DISC profile."""
        if primary == DISCDimension.DOMINANCE:
            return "Embraces change as opportunity for results"
        elif primary == DISCDimension.INFLUENCE:
            return "Enthusiastic about change with people involvement"
        elif primary == DISCDimension.STEADINESS:
            return "Resistant to change, needs time and support"
        else:  # CONSCIENTIOUSNESS
            return "Cautious about change, needs detailed planning"
    
    @classmethod
    def _get_team_contribution(cls, primary: DISCDimension, secondary: Optional[DISCDimension]) -> str:
        """Get team contribution based on DISC profile."""
        contributions = {
            DISCDimension.DOMINANCE: "Drives results and takes charge",
            DISCDimension.INFLUENCE: "Motivates team and builds relationships",
            DISCDimension.STEADINESS: "Provides stability and support",
            DISCDimension.CONSCIENTIOUSNESS: "Ensures quality and accuracy"
        }
        
        primary_contribution = contributions[primary]
        if secondary:
            secondary_contribution = contributions[secondary]
            return f"{primary_contribution} while {secondary_contribution.lower()}"
        return primary_contribution
    
    @classmethod
    def _get_development_areas(cls, primary: DISCDimension, secondary: Optional[DISCDimension]) -> List[str]:
        """Get development areas based on DISC profile."""
        development_areas = {
            DISCDimension.DOMINANCE: [
                "Develop patience with others",
                "Improve listening skills",
                "Consider team input in decisions",
                "Practice empathy and sensitivity"
            ],
            DISCDimension.INFLUENCE: [
                "Improve attention to detail",
                "Develop follow-through skills",
                "Practice active listening",
                "Focus on task completion"
            ],
            DISCDimension.STEADINESS: [
                "Develop assertiveness skills",
                "Practice speaking up in meetings",
                "Embrace change more readily",
                "Take on leadership roles"
            ],
            DISCDimension.CONSCIENTIOUSNESS: [
                "Develop risk-taking abilities",
                "Improve interpersonal skills",
                "Practice quick decision-making",
                "Focus on big picture thinking"
            ]
        }
        
        areas = development_areas[primary].copy()
        if secondary and secondary != primary:
            # Add complementary development areas
            areas.extend(development_areas[secondary][:2])
        
        return areas[:6]  # Limit to top 6
    
    @classmethod
    def get_question_data(cls) -> List[Dict[str, Any]]:
        """Get question data for frontend display."""
        return [
            {
                "id": question["id"],
                "instruction": question["instruction"],
                "words": [
                    {
                        "text": word["text"],
                        "index": i
                    }
                    for i, word in enumerate(question["words"])
                ],
                "type": "forced_choice",
                "required": True
            }
            for question in cls.QUESTIONS
        ]
    
    @classmethod
    def validate_response_set(cls, most_responses: List[int], least_responses: List[int]) -> Tuple[bool, List[str]]:
        """Validate DISC response sets."""
        errors = []
        
        if len(most_responses) != 28:
            errors.append(f"Expected 28 most responses, got {len(most_responses)}")
        
        if len(least_responses) != 28:
            errors.append(f"Expected 28 least responses, got {len(least_responses)}")
        
        for i, (most, least) in enumerate(zip(most_responses, least_responses)):
            if not isinstance(most, int) or not isinstance(least, int):
                errors.append(f"Question {i+1}: Responses must be integers")
                continue
            
            if not (0 <= most <= 3) or not (0 <= least <= 3):
                errors.append(f"Question {i+1}: Responses must be between 0 and 3")
                continue
            
            if most == least:
                errors.append(f"Question {i+1}: Most and least responses cannot be the same")
        
        return len(errors) == 0, errors
    
    @classmethod
    def create_database_template(cls, session: Session) -> TestTemplate:
        """Create DISC assessment template in the database."""
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
            description=f"DISC Behavioral Assessment - {cls.ADMINISTRATION_TIME}"
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        # Create questions (store as JSON for complex structure)
        for i, question_data in enumerate(cls.QUESTIONS):
            question = Question(
                template_id=template.id,
                text=question_data["instruction"],
                order=question_data["id"],
                min_value=0,
                max_value=3,
                weight=1.0,
                dimension_pair="DISC",
                positive_letter=None,
                show_if_question_id=None,
                show_if_value=None
            )
            session.add(question)
        
        session.commit()
        return template


# Convenience function
def calculate_disc_profile(most_responses: List[int], least_responses: List[int]) -> DISCResult:
    """Convenience function to calculate DISC profile."""
    return DISCAssessment.calculate_disc_profile(most_responses, least_responses)
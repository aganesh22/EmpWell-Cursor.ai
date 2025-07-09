"""
16 Personality Types (MBTI-inspired) Test Implementation.

This module provides a comprehensive personality assessment based on the Myers-Briggs Type Indicator
framework, measuring four dichotomies: Extraversion/Introversion, Sensing/Intuition, 
Thinking/Feeling, and Judging/Perceiving.

Note: This is an educational implementation inspired by MBTI concepts and should not be used
as a substitute for professional psychological assessment.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import random
from sqlmodel import Session

from backend.app.models import TestTemplate, Question, TestAttempt, Response


class PersonalityDimension(str, Enum):
    """The four personality dimensions."""
    EXTRAVERSION_INTROVERSION = "EI"
    SENSING_INTUITION = "SN"
    THINKING_FEELING = "TF"
    JUDGING_PERCEIVING = "JP"


class PersonalityType(str, Enum):
    """The 16 personality types."""
    # Analysts (NT)
    INTJ = "INTJ"  # The Architect
    INTP = "INTP"  # The Thinker
    ENTJ = "ENTJ"  # The Commander
    ENTP = "ENTP"  # The Debater
    
    # Diplomats (NF)
    INFJ = "INFJ"  # The Advocate
    INFP = "INFP"  # The Mediator
    ENFJ = "ENFJ"  # The Protagonist
    ENFP = "ENFP"  # The Campaigner
    
    # Sentinels (SJ)
    ISTJ = "ISTJ"  # The Logistician
    ISFJ = "ISFJ"  # The Protector
    ESTJ = "ESTJ"  # The Executive
    ESFJ = "ESFJ"  # The Consul
    
    # Explorers (SP)
    ISTP = "ISTP"  # The Virtuoso
    ISFP = "ISFP"  # The Adventurer
    ESTP = "ESTP"  # The Entrepreneur
    ESFP = "ESFP"  # The Entertainer


@dataclass
class PersonalityResult:
    """Result of personality assessment."""
    personality_type: PersonalityType
    dimension_scores: Dict[PersonalityDimension, float]
    dimension_preferences: Dict[PersonalityDimension, str]
    confidence_scores: Dict[PersonalityDimension, float]
    type_description: str
    strengths: List[str]
    potential_challenges: List[str]
    career_suggestions: List[str]
    relationship_insights: List[str]
    development_tips: List[str]


class PersonalityTest:
    """
    16 Personality Types Test Implementation.
    
    This test assesses personality across four dimensions:
    - Extraversion (E) vs Introversion (I)
    - Sensing (S) vs Intuition (N)
    - Thinking (T) vs Feeling (F)
    - Judging (J) vs Perceiving (P)
    """
    
    NAME = "16 Personality Types Assessment"
    KEY = "mbti16"
    VERSION = "1.0"
    ADMINISTRATION_TIME = "10-15 minutes"
    
    # Comprehensive question bank (60 questions, 15 per dimension)
    QUESTIONS = [
        # Extraversion/Introversion Questions (E/I)
        {
            "id": 1,
            "text": "I feel energized after spending time with a large group of people",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "energy_source"
        },
        {
            "id": 2,
            "text": "I prefer to think things through quietly before speaking",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "I",
            "category": "processing_style"
        },
        {
            "id": 3,
            "text": "I enjoy being the center of attention at social gatherings",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "social_preference"
        },
        {
            "id": 4,
            "text": "I need quiet time alone to recharge after social activities",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "I",
            "category": "energy_source"
        },
        {
            "id": 5,
            "text": "I think out loud and often talk through problems",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "processing_style"
        },
        {
            "id": 6,
            "text": "I prefer deep conversations with a few close friends",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "I",
            "category": "social_preference"
        },
        {
            "id": 7,
            "text": "I feel comfortable starting conversations with strangers",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "social_behavior"
        },
        {
            "id": 8,
            "text": "I often keep my thoughts and feelings to myself",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "I",
            "category": "expression_style"
        },
        {
            "id": 9,
            "text": "I enjoy meeting new people and making new connections",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "social_behavior"
        },
        {
            "id": 10,
            "text": "I prefer to observe before participating in group activities",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "I",
            "category": "participation_style"
        },
        {
            "id": 11,
            "text": "I often speak before thinking things through completely",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "processing_style"
        },
        {
            "id": 12,
            "text": "I prefer written communication over verbal communication",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "I",
            "category": "communication_style"
        },
        {
            "id": 13,
            "text": "I enjoy working in teams and collaborative environments",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "work_style"
        },
        {
            "id": 14,
            "text": "I do my best work when I can focus alone without interruptions",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "I",
            "category": "work_style"
        },
        {
            "id": 15,
            "text": "I tend to have a wide circle of friends and acquaintances",
            "dimension": PersonalityDimension.EXTRAVERSION_INTROVERSION,
            "direction": "E",
            "category": "social_network"
        },
        
        # Sensing/Intuition Questions (S/N)
        {
            "id": 16,
            "text": "I prefer to focus on concrete facts and details",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "information_processing"
        },
        {
            "id": 17,
            "text": "I enjoy exploring possibilities and imagining what could be",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "N",
            "category": "future_orientation"
        },
        {
            "id": 18,
            "text": "I trust my past experience more than theoretical possibilities",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "decision_basis"
        },
        {
            "id": 19,
            "text": "I often see patterns and connections that others miss",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "N",
            "category": "pattern_recognition"
        },
        {
            "id": 20,
            "text": "I prefer step-by-step instructions and clear procedures",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "learning_style"
        },
        {
            "id": 21,
            "text": "I enjoy brainstorming and generating new ideas",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "N",
            "category": "creativity"
        },
        {
            "id": 22,
            "text": "I notice small details that others often overlook",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "attention_to_detail"
        },
        {
            "id": 23,
            "text": "I'm more interested in the big picture than the details",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "N",
            "category": "perspective"
        },
        {
            "id": 24,
            "text": "I prefer practical, hands-on learning experiences",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "learning_style"
        },
        {
            "id": 25,
            "text": "I often think about future possibilities and potential outcomes",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "N",
            "category": "future_orientation"
        },
        {
            "id": 26,
            "text": "I value accuracy and precision in my work",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "work_values"
        },
        {
            "id": 27,
            "text": "I enjoy theoretical discussions and abstract concepts",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "N",
            "category": "conceptual_thinking"
        },
        {
            "id": 28,
            "text": "I prefer to work with established methods and proven techniques",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "methodology"
        },
        {
            "id": 29,
            "text": "I often come up with innovative solutions to problems",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "N",
            "category": "problem_solving"
        },
        {
            "id": 30,
            "text": "I trust information that comes from my five senses",
            "dimension": PersonalityDimension.SENSING_INTUITION,
            "direction": "S",
            "category": "information_trust"
        },
        
        # Thinking/Feeling Questions (T/F)
        {
            "id": 31,
            "text": "I make decisions based on logical analysis rather than personal values",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "decision_making"
        },
        {
            "id": 32,
            "text": "I consider how my decisions will affect other people's feelings",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "F",
            "category": "empathy"
        },
        {
            "id": 33,
            "text": "I value fairness and objective criteria in decision-making",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "fairness"
        },
        {
            "id": 34,
            "text": "I prefer harmony and avoid conflict when possible",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "F",
            "category": "conflict_style"
        },
        {
            "id": 35,
            "text": "I can easily separate my emotions from my reasoning",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "emotional_detachment"
        },
        {
            "id": 36,
            "text": "I find it important to maintain good relationships with others",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "F",
            "category": "relationship_focus"
        },
        {
            "id": 37,
            "text": "I enjoy debating and challenging others' ideas",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "intellectual_challenge"
        },
        {
            "id": 38,
            "text": "I often put others' needs before my own",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "F",
            "category": "altruism"
        },
        {
            "id": 39,
            "text": "I believe criticism is necessary for improvement",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "feedback_approach"
        },
        {
            "id": 40,
            "text": "I'm sensitive to other people's moods and emotions",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "F",
            "category": "emotional_awareness"
        },
        {
            "id": 41,
            "text": "I prefer to make decisions based on clear rules and principles",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "principle_based"
        },
        {
            "id": 42,
            "text": "I consider personal values and beliefs when making decisions",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "F",
            "category": "value_based"
        },
        {
            "id": 43,
            "text": "I can remain calm and objective in emotional situations",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "emotional_stability"
        },
        {
            "id": 44,
            "text": "I often act as a mediator in conflicts between others",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "F",
            "category": "mediation"
        },
        {
            "id": 45,
            "text": "I value competence and achievement over personal relationships",
            "dimension": PersonalityDimension.THINKING_FEELING,
            "direction": "T",
            "category": "priority_focus"
        },
        
        # Judging/Perceiving Questions (J/P)
        {
            "id": 46,
            "text": "I prefer to have a clear plan and stick to it",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "planning"
        },
        {
            "id": 47,
            "text": "I like to keep my options open and be flexible",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "P",
            "category": "flexibility"
        },
        {
            "id": 48,
            "text": "I feel uncomfortable when things are left unfinished",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "closure"
        },
        {
            "id": 49,
            "text": "I work well under pressure and tight deadlines",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "P",
            "category": "pressure_response"
        },
        {
            "id": 50,
            "text": "I prefer to make decisions quickly and move on",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "decision_speed"
        },
        {
            "id": 51,
            "text": "I enjoy exploring different options before making a decision",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "P",
            "category": "exploration"
        },
        {
            "id": 52,
            "text": "I like to have a structured schedule and routine",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "structure"
        },
        {
            "id": 53,
            "text": "I prefer spontaneity over detailed planning",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "P",
            "category": "spontaneity"
        },
        {
            "id": 54,
            "text": "I feel satisfied when I complete tasks on time",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "completion_satisfaction"
        },
        {
            "id": 55,
            "text": "I often start multiple projects but struggle to finish them",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "P",
            "category": "project_management"
        },
        {
            "id": 56,
            "text": "I prefer to have clear deadlines and expectations",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "expectations"
        },
        {
            "id": 57,
            "text": "I adapt easily to unexpected changes and new situations",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "P",
            "category": "adaptability"
        },
        {
            "id": 58,
            "text": "I like to organize my environment and keep things tidy",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "organization"
        },
        {
            "id": 59,
            "text": "I find it energizing to juggle multiple tasks at once",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "P",
            "category": "multitasking"
        },
        {
            "id": 60,
            "text": "I prefer to settle matters and reach conclusions",
            "dimension": PersonalityDimension.JUDGING_PERCEIVING,
            "direction": "J",
            "category": "resolution"
        }
    ]
    
    # Personality type descriptions
    TYPE_DESCRIPTIONS = {
        PersonalityType.INTJ: {
            "name": "The Architect",
            "description": "Imaginative and strategic thinkers, with a plan for everything.",
            "strengths": [
                "Independent and decisive",
                "Hard-working and determined",
                "Confident and versatile",
                "Strategic and analytical",
                "Highly competent"
            ],
            "challenges": [
                "May be overly analytical",
                "Can be judgmental of others",
                "May struggle with emotional expression",
                "Tendency to be perfectionistic",
                "May appear arrogant or dismissive"
            ],
            "careers": [
                "Architect or Engineer",
                "Research Scientist",
                "Strategic Planner",
                "Investment Banker",
                "Computer Systems Analyst",
                "University Professor"
            ],
            "relationships": [
                "Value intellectual compatibility",
                "Prefer deep, meaningful connections",
                "May struggle with small talk",
                "Appreciate partners who respect their independence"
            ],
            "development": [
                "Practice expressing emotions more openly",
                "Work on being more patient with others",
                "Develop better listening skills",
                "Learn to appreciate different perspectives"
            ]
        },
        PersonalityType.INTP: {
            "name": "The Thinker",
            "description": "Innovative inventors with an unquenchable thirst for knowledge.",
            "strengths": [
                "Highly analytical and objective",
                "Creative and innovative",
                "Independent and original",
                "Flexible and adaptable",
                "Intellectually curious"
            ],
            "challenges": [
                "May procrastinate on routine tasks",
                "Can be insensitive to others' feelings",
                "May struggle with follow-through",
                "Tendency to be overly critical",
                "May appear absent-minded"
            ],
            "careers": [
                "Software Developer",
                "Research Scientist",
                "Philosopher",
                "Mathematician",
                "Writer or Journalist",
                "University Professor"
            ],
            "relationships": [
                "Value intellectual stimulation",
                "Need space and independence",
                "May struggle with emotional intimacy",
                "Appreciate partners who share their interests"
            ],
            "development": [
                "Work on completing projects",
                "Practice being more considerate of others",
                "Develop better organizational skills",
                "Learn to express appreciation more often"
            ]
        },
        PersonalityType.ENTJ: {
            "name": "The Commander",
            "description": "Bold, imaginative and strong-willed leaders, always finding a way.",
            "strengths": [
                "Natural leader and organizer",
                "Confident and decisive",
                "Strategic and goal-oriented",
                "Efficient and productive",
                "Charismatic and inspiring"
            ],
            "challenges": [
                "May be impatient with inefficiency",
                "Can be overly critical",
                "May struggle with emotional sensitivity",
                "Tendency to be domineering",
                "May ignore others' feelings"
            ],
            "careers": [
                "CEO or Executive",
                "Management Consultant",
                "Lawyer",
                "Investment Banker",
                "Entrepreneur",
                "Political Leader"
            ],
            "relationships": [
                "Value competence and achievement",
                "Prefer partners who can keep up intellectually",
                "May struggle with emotional expression",
                "Appreciate direct communication"
            ],
            "development": [
                "Practice being more patient with others",
                "Work on emotional intelligence",
                "Learn to delegate more effectively",
                "Develop better listening skills"
            ]
        },
        PersonalityType.ENTP: {
            "name": "The Debater",
            "description": "Smart and curious thinkers who cannot resist an intellectual challenge.",
            "strengths": [
                "Quick-witted and clever",
                "Enthusiastic and energetic",
                "Innovative and creative",
                "Versatile and adaptable",
                "Excellent brainstormer"
            ],
            "challenges": [
                "May struggle with routine tasks",
                "Can be argumentative",
                "May have difficulty with follow-through",
                "Tendency to be disorganized",
                "May be insensitive to others' feelings"
            ],
            "careers": [
                "Entrepreneur",
                "Marketing Manager",
                "Journalist",
                "Consultant",
                "Inventor",
                "Sales Representative"
            ],
            "relationships": [
                "Value intellectual stimulation",
                "Enjoy debating and discussing ideas",
                "May struggle with emotional depth",
                "Appreciate partners who challenge them"
            ],
            "development": [
                "Work on following through on commitments",
                "Practice being more organized",
                "Develop better emotional sensitivity",
                "Learn to be more patient with routine tasks"
            ]
        },
        PersonalityType.INFJ: {
            "name": "The Advocate",
            "description": "Creative and insightful, inspired and independent perfectionists.",
            "strengths": [
                "Insightful and intuitive",
                "Principled and passionate",
                "Creative and imaginative",
                "Decisive and determined",
                "Inspiring and convincing"
            ],
            "challenges": [
                "May be overly sensitive",
                "Can be perfectionistic",
                "May struggle with criticism",
                "Tendency to be private",
                "May burnout from overcommitment"
            ],
            "careers": [
                "Counselor or Therapist",
                "Writer or Artist",
                "Human Resources Manager",
                "Social Worker",
                "Teacher or Professor",
                "Non-profit Leader"
            ],
            "relationships": [
                "Value deep, meaningful connections",
                "Highly empathetic and supportive",
                "May struggle with conflict",
                "Appreciate partners who understand their need for alone time"
            ],
            "development": [
                "Practice setting healthy boundaries",
                "Work on handling criticism better",
                "Develop more assertiveness",
                "Learn to take care of your own needs"
            ]
        },
        PersonalityType.INFP: {
            "name": "The Mediator",
            "description": "Poetic, kind and altruistic people, always eager to help good causes.",
            "strengths": [
                "Idealistic and loyal",
                "Adaptable and flexible",
                "Passionate and energetic",
                "Dedicated and hard-working",
                "Creative and imaginative"
            ],
            "challenges": [
                "May be overly idealistic",
                "Can be too self-critical",
                "May struggle with practical matters",
                "Tendency to take things personally",
                "May have difficulty with conflict"
            ],
            "careers": [
                "Writer or Poet",
                "Counselor or Therapist",
                "Artist or Designer",
                "Social Worker",
                "Teacher",
                "Non-profit Worker"
            ],
            "relationships": [
                "Value authenticity and harmony",
                "Deeply caring and supportive",
                "May avoid conflict",
                "Appreciate partners who share their values"
            ],
            "development": [
                "Practice being more assertive",
                "Work on practical skills",
                "Develop thicker skin for criticism",
                "Learn to balance idealism with realism"
            ]
        },
        PersonalityType.ENFJ: {
            "name": "The Protagonist",
            "description": "Charismatic and inspiring leaders, able to mesmerize listeners.",
            "strengths": [
                "Tolerant and reliable",
                "Charismatic and convincing",
                "Natural leader",
                "Passionate and energetic",
                "Altruistic and empathetic"
            ],
            "challenges": [
                "May be overly idealistic",
                "Can be too selfless",
                "May struggle with tough decisions",
                "Tendency to be too sensitive",
                "May fluctuate in self-esteem"
            ],
            "careers": [
                "Teacher or Professor",
                "Counselor or Therapist",
                "Human Resources Manager",
                "Social Worker",
                "Religious Leader",
                "Non-profit Manager"
            ],
            "relationships": [
                "Highly supportive and encouraging",
                "Value harmony and cooperation",
                "May neglect their own needs",
                "Appreciate partners who are equally caring"
            ],
            "development": [
                "Practice saying no and setting boundaries",
                "Work on taking care of your own needs",
                "Develop more objectivity",
                "Learn to handle conflict better"
            ]
        },
        PersonalityType.ENFP: {
            "name": "The Campaigner",
            "description": "Enthusiastic, creative and sociable free spirits, who can always find a reason to smile.",
            "strengths": [
                "Enthusiastic and energetic",
                "Creative and imaginative",
                "People-centered and warm",
                "Independent and flexible",
                "Excellent communication skills"
            ],
            "challenges": [
                "May struggle with routine tasks",
                "Can be overly emotional",
                "May have difficulty with follow-through",
                "Tendency to be disorganized",
                "May be overly optimistic"
            ],
            "careers": [
                "Marketing Manager",
                "Journalist",
                "Counselor or Therapist",
                "Teacher",
                "Actor or Performer",
                "Social Worker"
            ],
            "relationships": [
                "Warm and enthusiastic",
                "Value personal growth",
                "May struggle with routine",
                "Appreciate partners who share their enthusiasm"
            ],
            "development": [
                "Work on following through on commitments",
                "Practice being more organized",
                "Develop better focus",
                "Learn to handle routine tasks better"
            ]
        },
        PersonalityType.ISTJ: {
            "name": "The Logistician",
            "description": "Practical and fact-minded, reliable and responsible.",
            "strengths": [
                "Honest and direct",
                "Strong-willed and dutiful",
                "Very responsible",
                "Calm and practical",
                "Create and enforce order"
            ],
            "challenges": [
                "May be stubborn",
                "Can be insensitive",
                "May struggle with change",
                "Tendency to be judgmental",
                "May blame themselves unreasonably"
            ],
            "careers": [
                "Accountant",
                "Lawyer",
                "Military Officer",
                "Doctor",
                "Business Administrator",
                "Engineer"
            ],
            "relationships": [
                "Loyal and committed",
                "Value stability and tradition",
                "May struggle with expressing emotions",
                "Appreciate partners who are equally reliable"
            ],
            "development": [
                "Practice being more flexible",
                "Work on expressing emotions",
                "Develop better listening skills",
                "Learn to appreciate different perspectives"
            ]
        },
        PersonalityType.ISFJ: {
            "name": "The Protector",
            "description": "Warm-hearted and dedicated, always ready to protect loved ones.",
            "strengths": [
                "Supportive and reliable",
                "Patient and imaginative",
                "Loyal and hard-working",
                "Good practical skills",
                "Warm and sympathetic"
            ],
            "challenges": [
                "May be too modest",
                "Can be overly sensitive",
                "May struggle with change",
                "Tendency to repress feelings",
                "May be reluctant to innovate"
            ],
            "careers": [
                "Nurse or Healthcare Worker",
                "Teacher",
                "Social Worker",
                "Counselor",
                "Administrator",
                "Librarian"
            ],
            "relationships": [
                "Warm and caring",
                "Value harmony and stability",
                "May neglect their own needs",
                "Appreciate partners who are considerate"
            ],
            "development": [
                "Practice being more assertive",
                "Work on expressing your needs",
                "Develop more confidence",
                "Learn to embrace change"
            ]
        },
        PersonalityType.ESTJ: {
            "name": "The Executive",
            "description": "Excellent administrators, unsurpassed at managing things or people.",
            "strengths": [
                "Dedicated and strong-willed",
                "Direct and honest",
                "Loyal and patient",
                "Enjoy creating order",
                "Excellent organizers"
            ],
            "challenges": [
                "May be inflexible",
                "Can be judgmental",
                "May struggle with innovation",
                "Tendency to be too focused on status",
                "May be difficult to relax"
            ],
            "careers": [
                "Business Manager",
                "Military Officer",
                "Lawyer",
                "Judge",
                "Financial Officer",
                "Administrator"
            ],
            "relationships": [
                "Loyal and committed",
                "Value tradition and stability",
                "May struggle with emotional expression",
                "Appreciate partners who respect their authority"
            ],
            "development": [
                "Practice being more flexible",
                "Work on emotional intelligence",
                "Develop better listening skills",
                "Learn to appreciate different viewpoints"
            ]
        },
        PersonalityType.ESFJ: {
            "name": "The Consul",
            "description": "Extraordinarily caring, social and popular people, always eager to help.",
            "strengths": [
                "Strong practical skills",
                "Loyal and warm",
                "Good at connecting with others",
                "Dutiful and responsible",
                "Very supportive"
            ],
            "challenges": [
                "May worry too much about others",
                "Can be sensitive to criticism",
                "May struggle with change",
                "Tendency to be inflexible",
                "May neglect their own needs"
            ],
            "careers": [
                "Teacher",
                "Nurse or Healthcare Worker",
                "Social Worker",
                "Counselor",
                "Human Resources Manager",
                "Event Planner"
            ],
            "relationships": [
                "Warm and supportive",
                "Value harmony and cooperation",
                "May be overly accommodating",
                "Appreciate partners who are equally caring"
            ],
            "development": [
                "Practice setting boundaries",
                "Work on handling criticism better",
                "Develop more independence",
                "Learn to take care of your own needs"
            ]
        },
        PersonalityType.ISTP: {
            "name": "The Virtuoso",
            "description": "Bold and practical experimenters, masters of all kinds of tools.",
            "strengths": [
                "Optimistic and energetic",
                "Creative and practical",
                "Spontaneous and rational",
                "Know how to prioritize",
                "Great in a crisis"
            ],
            "challenges": [
                "May be stubborn",
                "Can be insensitive",
                "May struggle with commitment",
                "Tendency to be private",
                "May be easily bored"
            ],
            "careers": [
                "Engineer",
                "Mechanic",
                "Pilot",
                "Software Developer",
                "Athlete",
                "Photographer"
            ],
            "relationships": [
                "Loyal and supportive",
                "Value independence",
                "May struggle with emotional expression",
                "Appreciate partners who give them space"
            ],
            "development": [
                "Practice expressing emotions",
                "Work on long-term planning",
                "Develop better communication skills",
                "Learn to be more considerate of others"
            ]
        },
        PersonalityType.ISFP: {
            "name": "The Adventurer",
            "description": "Flexible and charming artists, always ready to explore new possibilities.",
            "strengths": [
                "Charming and sensitive",
                "Imaginative and passionate",
                "Curious and flexible",
                "Relaxed and warm",
                "Artistic and creative"
            ],
            "challenges": [
                "May be overly competitive",
                "Can be unpredictable",
                "May struggle with long-term planning",
                "Tendency to be easily stressed",
                "May be independent to a fault"
            ],
            "careers": [
                "Artist or Designer",
                "Musician",
                "Photographer",
                "Counselor",
                "Teacher",
                "Social Worker"
            ],
            "relationships": [
                "Warm and caring",
                "Value authenticity",
                "May avoid conflict",
                "Appreciate partners who understand their need for freedom"
            ],
            "development": [
                "Practice being more assertive",
                "Work on long-term planning",
                "Develop better organizational skills",
                "Learn to handle stress better"
            ]
        },
        PersonalityType.ESTP: {
            "name": "The Entrepreneur",
            "description": "Smart, energetic and perceptive people, truly enjoy living on the edge.",
            "strengths": [
                "Bold and rational",
                "Practical and original",
                "Perceptive and direct",
                "Sociable and popular",
                "Great in a crisis"
            ],
            "challenges": [
                "May be insensitive",
                "Can be impatient",
                "May struggle with theory",
                "Tendency to be risk-prone",
                "May be defiant"
            ],
            "careers": [
                "Entrepreneur",
                "Sales Representative",
                "Marketing Manager",
                "Police Officer",
                "Paramedic",
                "Real Estate Agent"
            ],
            "relationships": [
                "Fun and spontaneous",
                "Value excitement and adventure",
                "May struggle with emotional depth",
                "Appreciate partners who share their energy"
            ],
            "development": [
                "Practice being more patient",
                "Work on emotional sensitivity",
                "Develop better long-term planning",
                "Learn to think before acting"
            ]
        },
        PersonalityType.ESFP: {
            "name": "The Entertainer",
            "description": "Spontaneous, energetic and enthusiastic people - life is never boring.",
            "strengths": [
                "Bold and beautiful",
                "Original and aesthetic",
                "Showmanship and practical",
                "Observant and excellent people skills",
                "Popular and friendly"
            ],
            "challenges": [
                "May be sensitive and emotional",
                "Can be conflict-averse",
                "May struggle with focus",
                "Tendency to be easily bored",
                "May be poor long-term planners"
            ],
            "careers": [
                "Actor or Performer",
                "Event Planner",
                "Sales Representative",
                "Teacher",
                "Social Worker",
                "Tour Guide"
            ],
            "relationships": [
                "Warm and enthusiastic",
                "Value harmony and fun",
                "May avoid serious discussions",
                "Appreciate partners who enjoy life"
            ],
            "development": [
                "Practice focusing on long-term goals",
                "Work on handling conflict better",
                "Develop better organizational skills",
                "Learn to be more disciplined"
            ]
        }
    }
    
    @classmethod
    def calculate_personality_type(cls, responses: List[int]) -> PersonalityResult:
        """
        Calculate personality type from responses.
        
        Args:
            responses: List of integers (1-5) representing agreement levels
            
        Returns:
            PersonalityResult with type and detailed analysis
        """
        if len(responses) != 60:
            raise ValueError("Personality test requires exactly 60 responses")
        
        if not all(1 <= r <= 5 for r in responses):
            raise ValueError("All responses must be between 1 and 5")
        
        # Calculate dimension scores
        dimension_scores = {}
        dimension_preferences = {}
        confidence_scores = {}
        
        for dimension in PersonalityDimension:
            dimension_questions = [q for q in cls.QUESTIONS if q["dimension"] == dimension]
            
            e_or_s_or_t_or_j_score = 0
            i_or_n_or_f_or_p_score = 0
            
            for question in dimension_questions:
                response_value = responses[question["id"] - 1]  # Convert to 0-based index
                
                # Convert 1-5 scale to preference strength (-2 to +2)
                preference_strength = response_value - 3
                
                if question["direction"] in ["E", "S", "T", "J"]:
                    e_or_s_or_t_or_j_score += preference_strength
                else:  # I, N, F, P
                    i_or_n_or_f_or_p_score += preference_strength
            
            # Determine preference and confidence
            total_score = e_or_s_or_t_or_j_score - i_or_n_or_f_or_p_score
            
            if dimension == PersonalityDimension.EXTRAVERSION_INTROVERSION:
                if total_score > 0:
                    preference = "E"
                    confidence = abs(total_score) / 30.0  # Max possible score is 30
                else:
                    preference = "I"
                    confidence = abs(total_score) / 30.0
            elif dimension == PersonalityDimension.SENSING_INTUITION:
                if total_score > 0:
                    preference = "S"
                    confidence = abs(total_score) / 30.0
                else:
                    preference = "N"
                    confidence = abs(total_score) / 30.0
            elif dimension == PersonalityDimension.THINKING_FEELING:
                if total_score > 0:
                    preference = "T"
                    confidence = abs(total_score) / 30.0
                else:
                    preference = "F"
                    confidence = abs(total_score) / 30.0
            else:  # JUDGING_PERCEIVING
                if total_score > 0:
                    preference = "J"
                    confidence = abs(total_score) / 30.0
                else:
                    preference = "P"
                    confidence = abs(total_score) / 30.0
            
            dimension_scores[dimension] = total_score
            dimension_preferences[dimension] = preference
            confidence_scores[dimension] = min(confidence, 1.0)  # Cap at 1.0
        
        # Determine personality type
        type_string = (
            dimension_preferences[PersonalityDimension.EXTRAVERSION_INTROVERSION] +
            dimension_preferences[PersonalityDimension.SENSING_INTUITION] +
            dimension_preferences[PersonalityDimension.THINKING_FEELING] +
            dimension_preferences[PersonalityDimension.JUDGING_PERCEIVING]
        )
        
        personality_type = PersonalityType(type_string)
        type_info = cls.TYPE_DESCRIPTIONS[personality_type]
        
        return PersonalityResult(
            personality_type=personality_type,
            dimension_scores=dimension_scores,
            dimension_preferences=dimension_preferences,
            confidence_scores=confidence_scores,
            type_description=f"{type_info['name']}: {type_info['description']}",
            strengths=type_info["strengths"],
            potential_challenges=type_info["challenges"],
            career_suggestions=type_info["careers"],
            relationship_insights=type_info["relationships"],
            development_tips=type_info["development"]
        )
    
    @classmethod
    def get_question_data(cls) -> List[Dict[str, Any]]:
        """Get question data for frontend display."""
        return [
            {
                "id": question["id"],
                "text": question["text"],
                "dimension": question["dimension"].value,
                "direction": question["direction"],
                "category": question["category"],
                "type": "likert",
                "options": [
                    "Strongly Disagree",
                    "Disagree",
                    "Neutral",
                    "Agree", 
                    "Strongly Agree"
                ],
                "required": True,
                "reverse_scored": False
            }
            for question in cls.QUESTIONS
        ]
    
    @classmethod
    def validate_response_set(cls, responses: List[int]) -> Tuple[bool, List[str]]:
        """Validate a complete response set."""
        errors = []
        
        if len(responses) != 60:
            errors.append(f"Expected 60 responses, got {len(responses)}")
        
        for i, response in enumerate(responses):
            if not isinstance(response, int):
                errors.append(f"Response {i+1} must be an integer")
            elif not (1 <= response <= 5):
                errors.append(f"Response {i+1} must be between 1 and 5")
        
        return len(errors) == 0, errors
    
    @classmethod
    def create_database_template(cls, session: Session) -> TestTemplate:
        """Create personality test template in the database."""
        # Check if template already exists
        from sqlmodel import select
        existing = session.exec(
            select(TestTemplate).where(TestTemplate.key == cls.KEY)
        ).first()
        
        if existing:
            return existing
        
        # Create template
        template = TestTemplate(
            key=cls.KEY,
            name=cls.NAME,
            description=f"16 Personality Types Assessment - {cls.ADMINISTRATION_TIME}"
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
                min_value=1,
                max_value=5,
                weight=1.0,
                dimension_pair=question_data["dimension"].value,
                positive_letter=question_data["direction"],
                show_if_question_id=None,
                show_if_value=None
            )
            session.add(question)
        
        session.commit()
        return template


# Convenience function
def calculate_personality_type(responses: List[int]) -> PersonalityResult:
    """Convenience function to calculate personality type."""
    return PersonalityTest.calculate_personality_type(responses)
"""
Sample data for demonstrating branching logic functionality.

This module provides sample test templates with branching rules
for testing and demonstration purposes.
"""

from sqlmodel import Session
from backend.app.models import TestTemplate, Question


def create_sample_branching_assessment(session: Session) -> TestTemplate:
    """Create a sample assessment with complex branching logic."""
    
    # Create the template
    template = TestTemplate(
        key="wellbeing_branching",
        name="Adaptive Wellbeing Assessment",
        description="Dynamic assessment that adapts based on your responses"
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    
    # Question 1: Entry point - "How are you feeling today?"
    q1 = Question(
        template_id=template.id,
        text="How are you feeling today?",
        order=1,
        min_value=1,
        max_value=5,
        weight=1.0,
        dimension_pair=None,
        positive_letter=None,
        show_if_question_id=None,
        show_if_value=None
    )
    
    # Question 2: Always shown - "How often do you exercise?"
    q2 = Question(
        template_id=template.id,
        text="How often do you exercise per week?",
        order=2,
        min_value=0,
        max_value=7,
        weight=0.8,
        dimension_pair=None,
        positive_letter=None,
        show_if_question_id=None,
        show_if_value=None
    )
    
    # Question 3: Conditional - only if Q1 <= 2 (feeling low)
    q3 = Question(
        template_id=template.id,
        text="Have you been experiencing persistent sadness or anxiety?",
        order=3,
        min_value=1,
        max_value=4,
        weight=1.5,
        dimension_pair="DS",  # Depression Score
        positive_letter="D",
        show_if_question_id=None,  # Will be set after q1 is created
        show_if_value=2  # Show if Q1 <= 2
    )
    
    # Question 4: Conditional - only if Q1 >= 4 (feeling good)
    q4 = Question(
        template_id=template.id,
        text="What activities bring you the most joy and satisfaction?",
        order=4,
        min_value=1,
        max_value=5,
        weight=1.0,
        dimension_pair="WB",  # Wellbeing
        positive_letter="W",
        show_if_question_id=None,  # Will be set after q1 is created
        show_if_value=4  # Show if Q1 >= 4
    )
    
    # Question 5: Conditional - only if Q2 >= 3 (exercises regularly)
    q5 = Question(
        template_id=template.id,
        text="How would you rate your current physical fitness level?",
        order=5,
        min_value=1,
        max_value=5,
        weight=1.2,
        dimension_pair="PF",  # Physical Fitness
        positive_letter="P",
        show_if_question_id=None,  # Will be set after q2 is created
        show_if_value=3  # Show if Q2 >= 3
    )
    
    # Question 6: Conditional - only if Q3 exists AND Q3 >= 3 (high distress)
    q6 = Question(
        template_id=template.id,
        text="Have you considered seeking professional mental health support?",
        order=6,
        min_value=1,
        max_value=3,
        weight=2.0,
        dimension_pair="HS",  # Help Seeking
        positive_letter="H",
        show_if_question_id=None,  # Will be set after q3 is created
        show_if_value=3  # Show if Q3 >= 3
    )
    
    # Question 7: Always shown at the end
    q7 = Question(
        template_id=template.id,
        text="Overall, how satisfied are you with your current life situation?",
        order=7,
        min_value=1,
        max_value=10,
        weight=1.0,
        dimension_pair="OS",  # Overall Satisfaction
        positive_letter="O",
        show_if_question_id=None,
        show_if_value=None
    )
    
    # Question 8: Work-related conditional - only if Q7 <= 5 (low life satisfaction)
    q8 = Question(
        template_id=template.id,
        text="How satisfied are you with your work-life balance?",
        order=8,
        min_value=1,
        max_value=5,
        weight=1.1,
        dimension_pair="WL",  # Work-Life Balance
        positive_letter="W",
        show_if_question_id=None,  # Will be set after q7 is created
        show_if_value=5  # Show if Q7 <= 5
    )

    # Add all questions to session
    questions = [q1, q2, q3, q4, q5, q6, q7, q8]
    for q in questions:
        session.add(q)
    
    session.commit()
    
    # Refresh to get IDs
    for q in questions:
        session.refresh(q)
    
    # Set up conditional references now that we have IDs
    q3.show_if_question_id = q1.id
    q4.show_if_question_id = q1.id
    q5.show_if_question_id = q2.id
    q6.show_if_question_id = q3.id
    q8.show_if_question_id = q7.id
    
    session.commit()
    
    return template


def create_personality_branching_test(session: Session) -> TestTemplate:
    """Create a personality test with branching logic."""
    
    template = TestTemplate(
        key="personality_adaptive",
        name="Adaptive Personality Assessment",
        description="Personality test that adapts based on your responses"
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    
    # Core personality questions
    questions = [
        # Question 1: Social preference (determines introversion/extraversion branch)
        Question(
            template_id=template.id,
            text="I prefer spending time in large social gatherings",
            order=1,
            min_value=1,
            max_value=5,
            weight=1.0,
            dimension_pair="EI",  # Extraversion-Introversion
            positive_letter="E"
        ),
        
        # Question 2: Always shown - conscientiousness
        Question(
            template_id=template.id,
            text="I am highly organized and methodical in my approach",
            order=2,
            min_value=1,
            max_value=5,
            weight=1.0,
            dimension_pair="C",   # Conscientiousness
            positive_letter="C"
        ),
        
        # Question 3: Conditional - if Q1 >= 4 (extraverted), ask about leadership
        Question(
            template_id=template.id,
            text="I often take charge in group situations",
            order=3,
            min_value=1,
            max_value=5,
            weight=1.2,
            dimension_pair="EI",
            positive_letter="E",
            show_if_question_id=None,  # Will be set to Q1
            show_if_value=4
        ),
        
        # Question 4: Conditional - if Q1 <= 2 (introverted), ask about solitude
        Question(
            template_id=template.id,
            text="I find solitary activities energizing and fulfilling",
            order=4,
            min_value=1,
            max_value=5,
            weight=1.2,
            dimension_pair="EI",
            positive_letter="I",
            show_if_question_id=None,  # Will be set to Q1
            show_if_value=2
        ),
        
        # Question 5: Openness to experience
        Question(
            template_id=template.id,
            text="I actively seek out new and unusual experiences",
            order=5,
            min_value=1,
            max_value=5,
            weight=1.0,
            dimension_pair="O",   # Openness
            positive_letter="O"
        ),
        
        # Question 6: Conditional - if Q2 >= 4 (highly conscientious), ask about planning
        Question(
            template_id=template.id,
            text="I always plan activities well in advance",
            order=6,
            min_value=1,
            max_value=5,
            weight=1.3,
            dimension_pair="C",
            positive_letter="C",
            show_if_question_id=None,  # Will be set to Q2
            show_if_value=4
        )
    ]
    
    # Add all questions
    for q in questions:
        session.add(q)
    session.commit()
    
    # Refresh to get IDs
    for q in questions:
        session.refresh(q)
    
    # Set up conditional references
    questions[2].show_if_question_id = questions[0].id  # Q3 depends on Q1
    questions[3].show_if_question_id = questions[0].id  # Q4 depends on Q1
    questions[5].show_if_question_id = questions[1].id  # Q6 depends on Q2
    
    session.commit()
    
    return template


def create_stress_assessment_with_branching(session: Session) -> TestTemplate:
    """Create a stress assessment with targeted branching."""
    
    template = TestTemplate(
        key="stress_adaptive",
        name="Adaptive Stress Assessment",
        description="Stress assessment that focuses on your specific stressors"
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    
    questions = [
        # Question 1: Overall stress level
        Question(
            template_id=template.id,
            text="How stressed do you feel on a typical day?",
            order=1,
            min_value=1,
            max_value=5,
            weight=1.0,
            dimension_pair="GS",  # General Stress
            positive_letter="S"
        ),
        
        # Question 2: Work-related stress (if Q1 >= 3)
        Question(
            template_id=template.id,
            text="How much stress does your work or studies cause you?",
            order=2,
            min_value=1,
            max_value=5,
            weight=1.2,
            dimension_pair="WS",  # Work Stress
            positive_letter="W",
            show_if_question_id=None,  # Will be set to Q1
            show_if_value=3
        ),
        
        # Question 3: Relationship stress (if Q1 >= 3)
        Question(
            template_id=template.id,
            text="How much stress do your personal relationships cause you?",
            order=3,
            min_value=1,
            max_value=5,
            weight=1.1,
            dimension_pair="RS",  # Relationship Stress
            positive_letter="R",
            show_if_question_id=None,  # Will be set to Q1
            show_if_value=3
        ),
        
        # Question 4: Coping strategies (always shown)
        Question(
            template_id=template.id,
            text="How effectively do you handle stressful situations?",
            order=4,
            min_value=1,
            max_value=5,
            weight=1.0,
            dimension_pair="CS",  # Coping Strategies
            positive_letter="C"
        ),
        
        # Question 5: Sleep impact (if any stress category >= 4)
        Question(
            template_id=template.id,
            text="How much does stress affect your sleep quality?",
            order=5,
            min_value=1,
            max_value=5,
            weight=1.3,
            dimension_pair="SI",  # Sleep Impact
            positive_letter="S",
            show_if_question_id=None,  # Will be set to Q1
            show_if_value=4
        )
    ]
    
    # Add and configure questions
    for q in questions:
        session.add(q)
    session.commit()
    
    for q in questions:
        session.refresh(q)
    
    # Set up conditional references
    questions[1].show_if_question_id = questions[0].id  # Q2 depends on Q1
    questions[2].show_if_question_id = questions[0].id  # Q3 depends on Q1
    questions[4].show_if_question_id = questions[0].id  # Q5 depends on Q1
    
    session.commit()
    
    return template


def initialize_sample_branching_tests(session: Session):
    """Initialize all sample branching tests in the database."""
    
    try:
        # Check if sample tests already exist
        existing = session.exec(
            session.query(TestTemplate).where(
                TestTemplate.key.in_([
                    "wellbeing_branching",
                    "personality_adaptive", 
                    "stress_adaptive"
                ])
            )
        ).all()
        
        if existing:
            print(f"Sample branching tests already exist: {[t.key for t in existing]}")
            return existing
        
        # Create sample tests
        wellbeing_test = create_sample_branching_assessment(session)
        personality_test = create_personality_branching_test(session)
        stress_test = create_stress_assessment_with_branching(session)
        
        print("Created sample branching tests:")
        print(f"- {wellbeing_test.name} (key: {wellbeing_test.key})")
        print(f"- {personality_test.name} (key: {personality_test.key})")
        print(f"- {stress_test.name} (key: {stress_test.key})")
        
        return [wellbeing_test, personality_test, stress_test]
        
    except Exception as e:
        print(f"Error creating sample branching tests: {e}")
        session.rollback()
        return []
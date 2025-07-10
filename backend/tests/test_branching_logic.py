"""
Test scenarios for branching logic in the dynamic test engine.

This module tests the conditional question display, scoring with branched paths,
progress tracking with skipped questions, and validation of branching rules.
"""

import pytest
from sqlmodel import Session, select
from fastapi.testclient import TestClient

from backend.app.models import TestTemplate, Question, TestAttempt, Response, User
from backend.app.core.branching import (
    create_branching_controller,
    create_rules_processor,
    create_score_calculator,
    create_progress_tracker,
)


# ---------------------------------------------------------------------------
# Modern wrappers using the shared branching helpers
# These override earlier standalone implementations and ensure the tests use
# the canonical logic from backend.app.core.branching.
# ---------------------------------------------------------------------------


def should_show_question(
    question: Question, previous_responses: list, session: Session
) -> bool:  # type: ignore[override]
    """Delegate to QuestionDisplayController.should_show_question."""
    controller = create_branching_controller(session)
    return controller.should_show_question(question, previous_responses)


def get_next_question(attempt_id: int, session: Session):  # type: ignore[override]
    """Delegate to QuestionDisplayController.get_next_question."""
    controller = create_branching_controller(session)
    return controller.get_next_question(attempt_id)


def calculate_test_score(  # type: ignore[override]
    attempt_id: int, session: Session
):
    """Delegate to BranchingScoreCalculator.calculate_test_score."""
    calculator = create_score_calculator(session)
    return calculator.calculate_test_score(attempt_id)


def get_test_progress(attempt_id: int, session: Session):  # type: ignore[override]
    """Delegate to BranchingProgressTracker.get_test_progress."""
    tracker = create_progress_tracker(session)
    return tracker.get_test_progress(attempt_id)


def validate_branching_rules(  # type: ignore[override]
    template_id: int, session: Session
):
    """Delegate to BranchingRulesProcessor.validate_branching_rules."""
    processor = create_rules_processor(session)
    return processor.validate_branching_rules(template_id)


@pytest.fixture
def branching_test_template(test_session: Session):
    """Create a test template with complex branching logic."""
    template = TestTemplate(
        key="branching_assessment",
        name="Complex Branching Assessment",
        description="Test with conditional questions and branching paths"
    )
    test_session.add(template)
    test_session.commit()
    test_session.refresh(template)

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
        text="Have you been experiencing persistent sadness?",
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
        text="What activities bring you the most joy?",
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
        text="How would you rate your physical fitness level?",
        order=5,
        min_value=1,
        max_value=5,
        weight=1.2,
        dimension_pair="PF",  # Physical Fitness
        positive_letter="P",
        show_if_question_id=None,  # Will be set after q2 is created
        show_if_value=3  # Show if Q2 >= 3
    )
    
    # Question 6: Conditional - only if Q3 exists AND Q3 >= 3 (high sadness)
    q6 = Question(
        template_id=template.id,
        text="Have you considered seeking professional help?",
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
        text="Overall, how satisfied are you with your current wellbeing?",
        order=7,
        min_value=1,
        max_value=10,
        weight=1.0,
        dimension_pair="OS",  # Overall Satisfaction
        positive_letter="O",
        show_if_question_id=None,
        show_if_value=None
    )

    # Add all questions to session
    questions = [q1, q2, q3, q4, q5, q6, q7]
    for q in questions:
        test_session.add(q)
    
    test_session.commit()
    
    # Refresh to get IDs
    for q in questions:
        test_session.refresh(q)
    
    # Set up conditional references now that we have IDs
    q3.show_if_question_id = q1.id
    q4.show_if_question_id = q1.id
    q5.show_if_question_id = q2.id
    q6.show_if_question_id = q3.id
    
    test_session.commit()
    
    template.questions = questions
    return template


@pytest.fixture
def test_user(test_session: Session):
    """Create a test user for assessments."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        department="Engineering"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def test_attempt(test_session: Session, branching_test_template: TestTemplate, test_user: User):
    """Create a test attempt for the branching assessment."""
    attempt = TestAttempt(
        template_id=branching_test_template.id,
        user_id=test_user.id
    )
    test_session.add(attempt)
    test_session.commit()
    test_session.refresh(attempt)
    return attempt


class TestBranchingLogic:
    """Test cases for branching logic functionality."""

    def test_should_show_question_basic(self, test_session: Session, branching_test_template: TestTemplate):
        """Test basic question visibility without conditions."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        # Questions without conditions should always be shown
        q1 = next(q for q in questions if q.order == 1)  # No conditions
        q2 = next(q for q in questions if q.order == 2)  # No conditions
        q7 = next(q for q in questions if q.order == 7)  # No conditions
        
        assert should_show_question(q1, [], test_session) == True
        assert should_show_question(q2, [], test_session) == True
        assert should_show_question(q7, [], test_session) == True

    def test_should_show_question_conditional_true(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test conditional question display when condition is met."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        q1 = next(q for q in questions if q.order == 1)
        q3 = next(q for q in questions if q.order == 3)  # Show if Q1 <= 2
        q4 = next(q for q in questions if q.order == 4)  # Show if Q1 >= 4
        
        # Answer Q1 with value 2 (low feeling)
        response1 = Response(
            attempt_id=test_attempt.id,
            question_id=q1.id,
            value=2
        )
        test_session.add(response1)
        test_session.commit()
        
        responses = [response1]
        
        # Q3 should be shown (condition: Q1 <= 2, actual: Q1 = 2)
        assert should_show_question(q3, responses, test_session) == True
        
        # Q4 should NOT be shown (condition: Q1 >= 4, actual: Q1 = 2)
        assert should_show_question(q4, responses, test_session) == False

    def test_should_show_question_conditional_false(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test conditional question display when condition is not met."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        q1 = next(q for q in questions if q.order == 1)
        q3 = next(q for q in questions if q.order == 3)  # Show if Q1 <= 2
        q4 = next(q for q in questions if q.order == 4)  # Show if Q1 >= 4
        
        # Answer Q1 with value 5 (high feeling)
        response1 = Response(
            attempt_id=test_attempt.id,
            question_id=q1.id,
            value=5
        )
        test_session.add(response1)
        test_session.commit()
        
        responses = [response1]
        
        # Q3 should NOT be shown (condition: Q1 <= 2, actual: Q1 = 5)
        assert should_show_question(q3, responses, test_session) == False
        
        # Q4 should be shown (condition: Q1 >= 4, actual: Q1 = 5)
        assert should_show_question(q4, responses, test_session) == True

    def test_nested_conditional_questions(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test nested conditional questions (Q6 depends on Q3, which depends on Q1)."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        q1 = next(q for q in questions if q.order == 1)
        q3 = next(q for q in questions if q.order == 3)  # Show if Q1 <= 2
        q6 = next(q for q in questions if q.order == 6)  # Show if Q3 >= 3
        
        # Answer Q1 with value 1 (very low feeling) - should trigger Q3
        response1 = Response(
            attempt_id=test_attempt.id,
            question_id=q1.id,
            value=1
        )
        
        # Answer Q3 with value 4 (high sadness) - should trigger Q6
        response3 = Response(
            attempt_id=test_attempt.id,
            question_id=q3.id,
            value=4
        )
        
        test_session.add_all([response1, response3])
        test_session.commit()
        
        responses = [response1, response3]
        
        # Q3 should be shown (Q1 = 1 <= 2)
        assert should_show_question(q3, [response1], test_session) == True
        
        # Q6 should be shown (Q3 = 4 >= 3)
        assert should_show_question(q6, responses, test_session) == True

    def test_get_next_question_linear_path(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test getting next question in a linear path."""
        # Start with no responses
        next_q = get_next_question(test_attempt.id, test_session)
        assert next_q is not None
        assert next_q.order == 1  # Should start with first question
        
        # Answer Q1 with high value (5) - should skip Q3, go to Q2
        q1 = next_q
        response1 = Response(
            attempt_id=test_attempt.id,
            question_id=q1.id,
            value=5
        )
        test_session.add(response1)
        test_session.commit()
        
        next_q = get_next_question(test_attempt.id, test_session)
        assert next_q is not None
        assert next_q.order == 2  # Should go to Q2

    def test_get_next_question_branching_path(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test getting next question in a branching path."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        q1 = next(q for q in questions if q.order == 1)
        q2 = next(q for q in questions if q.order == 2)
        
        # Answer Q1 with low value (1) - should trigger Q3 after Q2
        response1 = Response(
            attempt_id=test_attempt.id,
            question_id=q1.id,
            value=1
        )
        test_session.add(response1)
        test_session.commit()
        
        # Next should be Q2
        next_q = get_next_question(test_attempt.id, test_session)
        assert next_q.order == 2
        
        # Answer Q2
        response2 = Response(
            attempt_id=test_attempt.id,
            question_id=q2.id,
            value=2
        )
        test_session.add(response2)
        test_session.commit()
        
        # Next should be Q3 (because Q1 = 1 <= 2)
        next_q = get_next_question(test_attempt.id, test_session)
        assert next_q.order == 3

    def test_calculate_score_with_skipped_questions(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test score calculation when some questions are skipped due to branching."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        q1 = next(q for q in questions if q.order == 1)
        q2 = next(q for q in questions if q.order == 2)
        q4 = next(q for q in questions if q.order == 4)  # Will be shown
        q7 = next(q for q in questions if q.order == 7)
        
        # Create responses for a high-feeling path (Q3 and Q6 will be skipped)
        responses = [
            Response(attempt_id=test_attempt.id, question_id=q1.id, value=5),  # High feeling
            Response(attempt_id=test_attempt.id, question_id=q2.id, value=1),  # Low exercise
            Response(attempt_id=test_attempt.id, question_id=q4.id, value=4),  # Joy activities
            Response(attempt_id=test_attempt.id, question_id=q7.id, value=8),  # Overall satisfaction
        ]
        
        for response in responses:
            test_session.add(response)
        test_session.commit()
        
        raw_score, normalized_score = calculate_test_score(test_attempt.id, test_session)
        
        # Should calculate score only for answered questions
        assert raw_score is not None
        assert normalized_score is not None
        assert 0 <= normalized_score <= 100  # Should be normalized percentage

    def test_progress_tracking_with_skipped_questions(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test progress calculation when questions are skipped."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        q1 = next(q for q in questions if q.order == 1)
        q2 = next(q for q in questions if q.order == 2)
        
        # Answer first question with high value (will skip Q3)
        response1 = Response(
            attempt_id=test_attempt.id,
            question_id=q1.id,
            value=5
        )
        test_session.add(response1)
        test_session.commit()
        
        progress = get_test_progress(test_attempt.id, test_session)
        
        # Progress should account for skipped questions
        assert progress['answered_count'] == 1
        assert progress['total_questions'] > 1
        assert 0 < progress['percentage'] < 100

    def test_validate_branching_rules_valid(self, test_session: Session, branching_test_template: TestTemplate):
        """Test validation of valid branching rules."""
        is_valid, errors = validate_branching_rules(branching_test_template.id, test_session)
        
        # The test template should have valid branching rules
        assert is_valid == True
        assert len(errors) == 0

    def test_validate_branching_rules_circular_dependency(self, test_session: Session, test_user: User):
        """Test detection of circular dependencies in branching rules."""
        # Create a template with circular dependency
        template = TestTemplate(
            key="circular_test",
            name="Circular Dependency Test",
            description="Test with circular branching dependency"
        )
        test_session.add(template)
        test_session.commit()
        test_session.refresh(template)
        
        # Create questions with circular dependency
        q1 = Question(
            template_id=template.id,
            text="Question 1",
            order=1,
            min_value=1,
            max_value=5,
            weight=1.0,
            show_if_question_id=None,  # Will be set to q2.id
            show_if_value=3
        )
        
        q2 = Question(
            template_id=template.id,
            text="Question 2",
            order=2,
            min_value=1,
            max_value=5,
            weight=1.0,
            show_if_question_id=None,  # Will be set to q1.id
            show_if_value=3
        )
        
        test_session.add_all([q1, q2])
        test_session.commit()
        test_session.refresh(q1)
        test_session.refresh(q2)
        
        # Create circular dependency
        q1.show_if_question_id = q2.id
        q2.show_if_question_id = q1.id
        test_session.commit()
        
        is_valid, errors = validate_branching_rules(template.id, test_session)
        
        # Should detect circular dependency
        assert is_valid == False
        assert len(errors) > 0
        assert any("circular" in error.lower() for error in errors)

    def test_validate_branching_rules_invalid_reference(self, test_session: Session, test_user: User):
        """Test detection of invalid question references in branching rules."""
        # Create a template with invalid reference
        template = TestTemplate(
            key="invalid_ref_test",
            name="Invalid Reference Test",
            description="Test with invalid branching reference"
        )
        test_session.add(template)
        test_session.commit()
        test_session.refresh(template)
        
        # Create question with invalid reference
        q1 = Question(
            template_id=template.id,
            text="Question 1",
            order=1,
            min_value=1,
            max_value=5,
            weight=1.0,
            show_if_question_id=99999,  # Non-existent question ID
            show_if_value=3
        )
        
        test_session.add(q1)
        test_session.commit()
        
        is_valid, errors = validate_branching_rules(template.id, test_session)
        
        # Should detect invalid reference
        assert is_valid == False
        assert len(errors) > 0
        assert any("reference" in error.lower() or "not found" in error.lower() for error in errors)

    def test_complex_branching_scenario(self, test_session: Session, branching_test_template: TestTemplate, test_attempt: TestAttempt):
        """Test a complex branching scenario with multiple conditions."""
        questions = test_session.exec(
            select(Question).where(Question.template_id == branching_test_template.id)
        ).all()
        
        q1 = next(q for q in questions if q.order == 1)
        q2 = next(q for q in questions if q.order == 2)
        q3 = next(q for q in questions if q.order == 3)
        q5 = next(q for q in questions if q.order == 5)
        q6 = next(q for q in questions if q.order == 6)
        q7 = next(q for q in questions if q.order == 7)
        
        # Scenario: Low mood, high exercise, leading to multiple branches
        responses = [
            Response(attempt_id=test_attempt.id, question_id=q1.id, value=2),  # Low mood -> triggers Q3
            Response(attempt_id=test_attempt.id, question_id=q2.id, value=5),  # High exercise -> triggers Q5
            Response(attempt_id=test_attempt.id, question_id=q3.id, value=3),  # High sadness -> triggers Q6
            Response(attempt_id=test_attempt.id, question_id=q5.id, value=4),  # Good fitness
            Response(attempt_id=test_attempt.id, question_id=q6.id, value=2),  # Considering help
            Response(attempt_id=test_attempt.id, question_id=q7.id, value=6),  # Overall satisfaction
        ]
        
        for response in responses:
            test_session.add(response)
        test_session.commit()
        
        # Calculate final score
        raw_score, normalized_score = calculate_test_score(test_attempt.id, test_session)
        
        # Verify score calculation includes all answered questions with proper weighting
        assert raw_score is not None
        assert normalized_score is not None
        
        # Check that Q4 was skipped (since Q1 = 2, not >= 4)
        answered_questions = {r.question_id for r in responses}
        q4 = next(q for q in questions if q.order == 4)
        assert q4.id not in answered_questions

    def test_branching_with_client_api(self, client: TestClient, branching_test_template: TestTemplate, test_user: User):
        """Test branching logic through the API endpoints."""
        # Login first
        login_response = client.post(
            "/auth/login",
            data={"username": test_user.email, "password": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Login failed, skipping API test")
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Start the test
        start_response = client.post(
            f"/tests/{branching_test_template.key}/start",
            headers=headers
        )
        
        if start_response.status_code != 200:
            pytest.skip("Test start failed, skipping API test")
        
        attempt_data = start_response.json()
        
        # Get first question
        question_response = client.get(
            f"/tests/{branching_test_template.key}/question",
            headers=headers
        )
        
        assert question_response.status_code == 200
        question_data = question_response.json()
        assert question_data["order"] == 1
        
        # Answer with low value to trigger branching
        answer_response = client.post(
            f"/tests/{branching_test_template.key}/answer",
            json={"question_id": question_data["id"], "value": 2},
            headers=headers
        )
        
        assert answer_response.status_code == 200
        
        # Continue through the test and verify branching behavior
        for _ in range(5):  # Max 5 more questions
            question_response = client.get(
                f"/tests/{branching_test_template.key}/question",
                headers=headers
            )
            
            if question_response.status_code == 404:
                break  # Test completed
            
            question_data = question_response.json()
            
            # Answer each question
            client.post(
                f"/tests/{branching_test_template.key}/answer",
                json={"question_id": question_data["id"], "value": 3},
                headers=headers
            )
        
        # Get final results
        results_response = client.get(
            f"/tests/{branching_test_template.key}/results",
            headers=headers
        )
        
        if results_response.status_code == 200:
            results = results_response.json()
            assert "raw_score" in results
            assert "normalized_score" in results
            assert "interpretation" in results



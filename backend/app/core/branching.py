"""
Core branching logic for the dynamic test engine.

This module provides functionality for:
1. Question display controller - determines which questions to show
2. Branching rules processor - evaluates conditional logic
3. Scoring integration - handles scoring with branched paths
4. Progress tracking - calculates progress with skipped questions
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from sqlmodel import Session, select
from enum import Enum

from backend.app.models import Question, Response, TestAttempt, TestTemplate


class BranchingOperator(str, Enum):
    """Supported operators for branching conditions."""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN_RANGE = "in_range"
    NOT_IN_RANGE = "not_in_range"


class BranchingCondition:
    """Represents a single branching condition."""
    
    def __init__(
        self,
        question_id: int,
        operator: BranchingOperator,
        value: Any,
        value_max: Optional[Any] = None
    ):
        self.question_id = question_id
        self.operator = operator
        self.value = value
        self.value_max = value_max
    
    def evaluate(self, response_value: Any) -> bool:
        """Evaluate this condition against a response value."""
        if response_value is None:
            return False
        
        if self.operator == BranchingOperator.EQUALS:
            return response_value == self.value
        elif self.operator == BranchingOperator.NOT_EQUALS:
            return response_value != self.value
        elif self.operator == BranchingOperator.GREATER_THAN:
            return response_value > self.value
        elif self.operator == BranchingOperator.GREATER_THAN_OR_EQUAL:
            return response_value >= self.value
        elif self.operator == BranchingOperator.LESS_THAN:
            return response_value < self.value
        elif self.operator == BranchingOperator.LESS_THAN_OR_EQUAL:
            return response_value <= self.value
        elif self.operator == BranchingOperator.IN_RANGE:
            return self.value <= response_value <= (self.value_max or self.value)
        elif self.operator == BranchingOperator.NOT_IN_RANGE:
            return not (self.value <= response_value <= (self.value_max or self.value))
        
        return False


class BranchingRule:
    """Represents a complex branching rule with multiple conditions."""
    
    def __init__(
        self,
        conditions: List[BranchingCondition],
        logic_operator: str = "AND"  # "AND" or "OR"
    ):
        self.conditions = conditions
        self.logic_operator = logic_operator.upper()
    
    def evaluate(self, responses: Dict[int, Any]) -> bool:
        """Evaluate all conditions in this rule."""
        if not self.conditions:
            return True
        
        results = []
        for condition in self.conditions:
            response_value = responses.get(condition.question_id)
            results.append(condition.evaluate(response_value))
        
        if self.logic_operator == "OR":
            return any(results)
        else:  # Default to AND
            return all(results)


class QuestionDisplayController:
    """Controls which questions should be displayed based on branching logic."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def should_show_question(
        self,
        question: Question,
        previous_responses: List[Response]
    ) -> bool:
        """
        Determine if a question should be shown based on branching conditions.
        
        Args:
            question: The question to evaluate
            previous_responses: List of previous responses in this attempt
            
        Returns:
            True if question should be shown, False otherwise
        """
        # If no branching condition, always show
        if question.show_if_question_id is None:
            return True
        
        # Find the response for the conditional question
        conditional_response = None
        for response in previous_responses:
            if response.question_id == question.show_if_question_id:
                conditional_response = response
                break
        
        if conditional_response is None:
            return False  # Conditional question not answered yet
        
        # Evaluate the condition
        return self._evaluate_simple_condition(
            conditional_response.value,
            question.show_if_value
        )
    
    def _evaluate_simple_condition(self, response_value: int, threshold: int) -> bool:
        """
        Evaluate a simple branching condition using intelligent threshold logic.
        
        For backward compatibility with the existing model structure.
        """
        if threshold is None:
            return True
        
        # Smart threshold evaluation:
        # - Low threshold values (≤ 3) use ≤ comparison
        # - High threshold values (> 3) use ≥ comparison
        if threshold <= 3:
            return response_value <= threshold
        else:
            return response_value >= threshold
    
    def get_visible_questions(
        self,
        template_id: int,
        previous_responses: List[Response]
    ) -> List[Question]:
        """
        Get all questions that should be visible given the current responses.
        
        Args:
            template_id: The test template ID
            previous_responses: List of previous responses
            
        Returns:
            List of questions that should be shown
        """
        # Get all questions for this template, ordered
        all_questions = self.session.exec(
            select(Question)
            .where(Question.template_id == template_id)
            .order_by(Question.order)
        ).all()
        
        visible_questions = []
        for question in all_questions:
            if self.should_show_question(question, previous_responses):
                visible_questions.append(question)
        
        return visible_questions
    
    def get_next_question(self, attempt_id: int) -> Optional[Question]:
        """
        Get the next question to show in a test attempt.
        
        Args:
            attempt_id: The test attempt ID
            
        Returns:
            Next question to show, or None if test is complete
        """
        # Get the attempt
        attempt = self.session.get(TestAttempt, attempt_id)
        if not attempt:
            return None
        
        # Get existing responses
        existing_responses = self.session.exec(
            select(Response).where(Response.attempt_id == attempt_id)
        ).all()
        
        answered_question_ids = {r.question_id for r in existing_responses}
        
        # Get visible questions
        visible_questions = self.get_visible_questions(
            attempt.template_id,
            existing_responses
        )
        
        # Find first unanswered visible question
        for question in visible_questions:
            if question.id not in answered_question_ids:
                return question
        
        return None  # No more questions


class BranchingRulesProcessor:
    """Processes and validates branching rules for test templates."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def validate_branching_rules(self, template_id: int) -> Tuple[bool, List[str]]:
        """
        Validate the branching rules for a test template.
        
        Args:
            template_id: The test template ID
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Get all questions for this template
        questions = self.session.exec(
            select(Question).where(Question.template_id == template_id)
        ).all()
        
        question_map = {q.id: q for q in questions}
        
        # Check for circular dependencies
        circular_errors = self._check_circular_dependencies(questions, question_map)
        errors.extend(circular_errors)
        
        # Check for invalid references
        reference_errors = self._check_invalid_references(questions, question_map)
        errors.extend(reference_errors)
        
        # Check for logical inconsistencies
        logic_errors = self._check_logical_inconsistencies(questions, question_map)
        errors.extend(logic_errors)
        
        return len(errors) == 0, errors
    
    def _check_circular_dependencies(
        self,
        questions: List[Question],
        question_map: Dict[int, Question]
    ) -> List[str]:
        """Check for circular dependencies in branching rules."""
        errors = []
        
        def has_circular_dependency(
            question_id: int,
            visited: Set[int],
            recursion_stack: Set[int]
        ) -> bool:
            if question_id in recursion_stack:
                return True
            
            if question_id in visited:
                return False
            
            visited.add(question_id)
            recursion_stack.add(question_id)
            
            question = question_map.get(question_id)
            if question and question.show_if_question_id:
                if has_circular_dependency(
                    question.show_if_question_id,
                    visited,
                    recursion_stack
                ):
                    return True
            
            recursion_stack.remove(question_id)
            return False
        
        visited = set()
        for question in questions:
            if question.id not in visited:
                if has_circular_dependency(question.id, visited, set()):
                    errors.append(
                        f"Circular dependency detected involving question {question.id} "
                        f"('{question.text[:50]}...')"
                    )
        
        return errors
    
    def _check_invalid_references(
        self,
        questions: List[Question],
        question_map: Dict[int, Question]
    ) -> List[str]:
        """Check for invalid question references."""
        errors = []
        
        for question in questions:
            if question.show_if_question_id is not None:
                if question.show_if_question_id not in question_map:
                    errors.append(
                        f"Question {question.id} ('{question.text[:50]}...') "
                        f"references non-existent question {question.show_if_question_id}"
                    )
        
        return errors
    
    def _check_logical_inconsistencies(
        self,
        questions: List[Question],
        question_map: Dict[int, Question]
    ) -> List[str]:
        """Check for logical inconsistencies in branching rules."""
        errors = []
        
        for question in questions:
            if (question.show_if_question_id is not None and 
                question.show_if_value is not None):
                
                ref_question = question_map.get(question.show_if_question_id)
                if ref_question:
                    if (question.show_if_value < ref_question.min_value or 
                        question.show_if_value > ref_question.max_value):
                        errors.append(
                            f"Question {question.id} has invalid condition value "
                            f"{question.show_if_value} for referenced question range "
                            f"[{ref_question.min_value}, {ref_question.max_value}]"
                        )
        
        return errors
    
    def get_branching_tree(self, template_id: int) -> Dict[str, Any]:
        """
        Generate a visual representation of the branching tree.
        
        Args:
            template_id: The test template ID
            
        Returns:
            Dictionary representing the branching structure
        """
        questions = self.session.exec(
            select(Question)
            .where(Question.template_id == template_id)
            .order_by(Question.order)
        ).all()
        
        tree = {
            "template_id": template_id,
            "questions": [],
            "branches": []
        }
        
        for question in questions:
            question_node = {
                "id": question.id,
                "order": question.order,
                "text": question.text,
                "always_shown": question.show_if_question_id is None,
                "condition": None
            }
            
            if question.show_if_question_id is not None:
                question_node["condition"] = {
                    "depends_on_question": question.show_if_question_id,
                    "threshold_value": question.show_if_value,
                    "operator": "lte" if (question.show_if_value or 0) <= 3 else "gte"
                }
            
            tree["questions"].append(question_node)
        
        return tree


class BranchingScoreCalculator:
    """Handles score calculation for tests with branching logic."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_test_score(self, attempt_id: int) -> Tuple[float, float]:
        """
        Calculate the raw and normalized scores for a test attempt with branching.
        
        Args:
            attempt_id: The test attempt ID
            
        Returns:
            Tuple of (raw_score, normalized_score)
        """
        # Get attempt and responses
        attempt = self.session.get(TestAttempt, attempt_id)
        if not attempt:
            return 0.0, 0.0
        
        responses = self.session.exec(
            select(Response).where(Response.attempt_id == attempt_id)
        ).all()
        
        if not responses:
            return 0.0, 0.0
        
        # Get questions to access weights
        question_ids = [r.question_id for r in responses]
        questions = self.session.exec(
            select(Question).where(Question.id.in_(question_ids))
        ).all()
        
        question_map = {q.id: q for q in questions}
        
        # Calculate weighted score
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for response in responses:
            question = question_map.get(response.question_id)
            if question:
                # Normalize response value to 0-1 scale
                value_range = question.max_value - question.min_value
                if value_range > 0:
                    normalized_value = (response.value - question.min_value) / value_range
                else:
                    normalized_value = 0.0
                
                weighted_value = normalized_value * question.weight
                
                total_weighted_score += weighted_value
                total_weight += question.weight
        
        raw_score = total_weighted_score
        normalized_score = (
            (total_weighted_score / total_weight * 100) 
            if total_weight > 0 else 0.0
        )
        
        return raw_score, normalized_score
    
    def calculate_dimensional_scores(
        self,
        attempt_id: int
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate dimensional scores for personality tests or multi-dimensional assessments.
        
        Args:
            attempt_id: The test attempt ID
            
        Returns:
            Dictionary with dimensional scores
        """
        # Get attempt and responses
        attempt = self.session.get(TestAttempt, attempt_id)
        if not attempt:
            return {}
        
        responses = self.session.exec(
            select(Response).where(Response.attempt_id == attempt_id)
        ).all()
        
        if not responses:
            return {}
        
        # Get questions to access dimension pairs
        question_ids = [r.question_id for r in responses]
        questions = self.session.exec(
            select(Question).where(Question.id.in_(question_ids))
        ).all()
        
        question_map = {q.id: q for q in questions}
        
        # Group responses by dimension
        dimensional_scores = {}
        
        for response in responses:
            question = question_map.get(response.question_id)
            if question and question.dimension_pair:
                dimension = question.dimension_pair
                
                if dimension not in dimensional_scores:
                    dimensional_scores[dimension] = {
                        "raw_score": 0.0,
                        "total_weight": 0.0,
                        "question_count": 0,
                        "positive_letter": question.positive_letter
                    }
                
                # Normalize response value
                value_range = question.max_value - question.min_value
                if value_range > 0:
                    normalized_value = (response.value - question.min_value) / value_range
                else:
                    normalized_value = 0.0
                
                weighted_value = normalized_value * question.weight
                
                dimensional_scores[dimension]["raw_score"] += weighted_value
                dimensional_scores[dimension]["total_weight"] += question.weight
                dimensional_scores[dimension]["question_count"] += 1
        
        # Calculate normalized scores for each dimension
        for dimension, scores in dimensional_scores.items():
            if scores["total_weight"] > 0:
                scores["normalized_score"] = (
                    scores["raw_score"] / scores["total_weight"] * 100
                )
            else:
                scores["normalized_score"] = 0.0
        
        return dimensional_scores


class BranchingProgressTracker:
    """Tracks progress through tests with branching logic."""
    
    def __init__(self, session: Session):
        self.session = session
        self.display_controller = QuestionDisplayController(session)
    
    def get_test_progress(self, attempt_id: int) -> Dict[str, Any]:
        """
        Calculate test progress accounting for skipped questions due to branching.
        
        Args:
            attempt_id: The test attempt ID
            
        Returns:
            Dictionary with progress information
        """
        attempt = self.session.get(TestAttempt, attempt_id)
        if not attempt:
            return {"percentage": 0, "answered_count": 0, "total_questions": 0}
        
        # Get all responses so far
        responses = self.session.exec(
            select(Response).where(Response.attempt_id == attempt_id)
        ).all()
        
        # Get visible questions based on current responses
        visible_questions = self.display_controller.get_visible_questions(
            attempt.template_id,
            responses
        )
        
        answered_questions = len(responses)
        total_visible = len(visible_questions)
        
        # Estimate remaining questions that might become visible
        # This is an approximation since future answers might change the branching
        all_questions = self.session.exec(
            select(Question)
            .where(Question.template_id == attempt.template_id)
            .order_by(Question.order)
        ).all()
        
        conditional_questions = [
            q for q in all_questions 
            if q.show_if_question_id is not None
        ]
        
        # Estimate potential additional questions based on branching patterns
        potential_additional = len(conditional_questions) - sum(
            1 for q in conditional_questions if q in visible_questions
        )
        
        # Use a conservative estimate for total questions
        estimated_total = max(total_visible, answered_questions + 1)
        
        percentage = min(
            (answered_questions / estimated_total * 100) if estimated_total > 0 else 0,
            100
        )
        
        return {
            "percentage": percentage,
            "answered_count": answered_questions,
            "total_questions": estimated_total,
            "visible_questions": total_visible,
            "potential_additional": potential_additional,
            "is_complete": self.display_controller.get_next_question(attempt_id) is None
        }
    
    def get_question_path(self, attempt_id: int) -> List[Dict[str, Any]]:
        """
        Get the path of questions taken in this attempt.
        
        Args:
            attempt_id: The test attempt ID
            
        Returns:
            List of question path information
        """
        attempt = self.session.get(TestAttempt, attempt_id)
        if not attempt:
            return []
        
        responses = self.session.exec(
            select(Response)
            .where(Response.attempt_id == attempt_id)
            .join(Question)
            .order_by(Question.order)
        ).all()
        
        path = []
        for response in responses:
            question = self.session.get(Question, response.question_id)
            if question:
                path_item = {
                    "question_id": question.id,
                    "order": question.order,
                    "text": question.text,
                    "response_value": response.value,
                    "was_conditional": question.show_if_question_id is not None,
                    "condition_met": True  # Since it was answered
                }
                path.append(path_item)
        
        return path


# Convenience functions for easy integration
def create_branching_controller(session: Session) -> QuestionDisplayController:
    """Create a question display controller instance."""
    return QuestionDisplayController(session)


def create_rules_processor(session: Session) -> BranchingRulesProcessor:
    """Create a branching rules processor instance."""
    return BranchingRulesProcessor(session)


def create_score_calculator(session: Session) -> BranchingScoreCalculator:
    """Create a branching score calculator instance."""
    return BranchingScoreCalculator(session)


def create_progress_tracker(session: Session) -> BranchingProgressTracker:
    """Create a branching progress tracker instance."""
    return BranchingProgressTracker(session)
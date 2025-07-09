"""
Test DISC module imports and basic functionality.
"""

import pytest


def test_disc_imports():
    """Test that DISC module can be imported correctly."""
    from backend.app.core.disc_assessment import DISCAssessment, DISCDimension, calculate_disc_profile
    
    # Test that we can access the assessment class
    assert DISCAssessment is not None
    assert hasattr(DISCAssessment, 'QUESTIONS')
    assert len(DISCAssessment.QUESTIONS) == 28
    
    # Test that dimensions are available
    assert DISCDimension.DOMINANCE == "D"
    assert DISCDimension.INFLUENCE == "I"
    assert DISCDimension.STEADINESS == "S"
    assert DISCDimension.CONSCIENTIOUSNESS == "C"
    
    # Test that convenience function is available
    assert calculate_disc_profile is not None


def test_disc_basic_functionality():
    """Test basic DISC functionality without database dependencies."""
    from backend.app.core.disc_assessment import DISCAssessment
    
    # Test question data generation
    questions = DISCAssessment.get_question_data()
    assert len(questions) == 28
    assert all('id' in q for q in questions)
    assert all('instruction' in q for q in questions)
    assert all('words' in q for q in questions)
    assert all(len(q['words']) == 4 for q in questions)
    
    # Test validation
    most_responses = [0, 1, 2, 3] * 7
    least_responses = [3, 2, 1, 0] * 7
    
    is_valid, errors = DISCAssessment.validate_response_set(most_responses, least_responses)
    assert is_valid is True
    assert len(errors) == 0
    
    # Test invalid validation
    invalid_most = [0, 1, 2]  # Too few
    invalid_least = [3, 2, 1, 0] * 7
    
    is_valid, errors = DISCAssessment.validate_response_set(invalid_most, invalid_least)
    assert is_valid is False
    assert len(errors) > 0


def test_disc_calculation():
    """Test DISC profile calculation."""
    from backend.app.core.disc_assessment import calculate_disc_profile, DISCDimension
    
    # Test with sample data
    most_responses = [0, 1, 2, 3] * 7
    least_responses = [3, 2, 1, 0] * 7
    
    result = calculate_disc_profile(most_responses, least_responses)
    
    # Test result structure
    assert hasattr(result, 'primary_style')
    assert hasattr(result, 'dimension_percentages')
    assert hasattr(result, 'strengths')
    assert hasattr(result, 'potential_challenges')
    
    # Test that primary style is valid
    assert result.primary_style in DISCDimension
    
    # Test that percentages are valid
    assert len(result.dimension_percentages) == 4
    assert all(p >= 0 for p in result.dimension_percentages.values())
    
    # Test that lists are properly limited
    assert len(result.strengths) <= 8
    assert len(result.potential_challenges) <= 6
#!/usr/bin/env python3
"""
Standalone test for DISC Assessment implementation.
This test verifies core functionality without requiring external dependencies.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Mock the sqlmodel imports to avoid dependency issues
class MockSession:
    pass

class MockSelect:
    pass

# Mock the models
class MockTestTemplate:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockTestAttempt:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockResponse:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockUser:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

# Mock the modules
sys.modules['sqlmodel'] = type('MockModule', (), {
    'Session': MockSession,
    'select': MockSelect
})()

sys.modules['backend.app.models'] = type('MockModule', (), {
    'TestTemplate': MockTestTemplate,
    'TestAttempt': MockTestAttempt, 
    'Response': MockResponse,
    'User': MockUser
})()

# Now import the DISC assessment
from backend.app.core.disc_assessment import DISCAssessment, calculate_disc_profile, DISCDimension

def test_disc_assessment():
    """Test the DISC assessment implementation."""
    print("Testing DISC Assessment Implementation...")
    print("=" * 50)
    
    # Test 1: Question count
    questions = DISCAssessment.get_question_data()
    assert len(questions) == 28, f"Expected 28 questions, got {len(questions)}"
    print(f"✓ Question count: {len(questions)} questions")
    
    # Test 2: Question structure
    for i, question in enumerate(questions):
        assert question["id"] == i + 1, f"Question {i+1} has wrong ID"
        assert "instruction" in question, f"Question {i+1} missing instruction"
        assert "words" in question, f"Question {i+1} missing words"
        assert len(question["words"]) == 4, f"Question {i+1} doesn't have 4 words"
        assert question["type"] == "forced_choice", f"Question {i+1} wrong type"
        assert question["required"] is True, f"Question {i+1} not required"
    print("✓ Question structure validation passed")
    
    # Test 3: Dimension coverage
    dimensions_found = set()
    for question in DISCAssessment.QUESTIONS:
        for word in question["words"]:
            dimensions_found.add(word["dimension"])
    
    expected_dimensions = set(DISCDimension)
    assert dimensions_found == expected_dimensions, "Not all DISC dimensions represented"
    print(f"✓ All DISC dimensions represented: {[d.value for d in dimensions_found]}")
    
    # Test 4: Scoring with sample data
    most_responses = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
    least_responses = [3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0]
    
    result = calculate_disc_profile(most_responses, least_responses)
    
    assert result.primary_style in DISCDimension, "Invalid primary style"
    assert result.intensity_level in ["High", "Moderate", "Low"], "Invalid intensity level"
    assert len(result.strengths) <= 8, "Too many strengths"
    assert len(result.potential_challenges) <= 6, "Too many challenges"
    assert len(result.development_areas) <= 6, "Too many development areas"
    
    print(f"✓ Scoring algorithm: Primary style = {result.primary_style.value}")
    print(f"✓ Profile type: {result.profile_type.value}")
    print(f"✓ Intensity level: {result.intensity_level}")
    print(f"✓ Strengths count: {len(result.strengths)}")
    print(f"✓ Challenges count: {len(result.potential_challenges)}")
    
    # Test 5: Validation
    is_valid, errors = DISCAssessment.validate_response_set(most_responses, least_responses)
    assert is_valid is True, f"Valid responses failed validation: {errors}"
    assert len(errors) == 0, f"Valid responses produced errors: {errors}"
    print(f"✓ Validation: {is_valid} (errors: {len(errors)})")
    
    # Test 6: Invalid responses
    invalid_most = [0, 1, 2]  # Too few
    invalid_least = [3, 2, 1, 0] * 7  # Correct length
    
    is_valid, errors = DISCAssessment.validate_response_set(invalid_most, invalid_least)
    assert is_valid is False, "Invalid responses passed validation"
    assert len(errors) > 0, "Invalid responses produced no errors"
    print(f"✓ Invalid response validation: {is_valid} (errors: {len(errors)})")
    
    # Test 7: Dimension percentages
    percentages = result.dimension_percentages
    assert len(percentages) == 4, "Wrong number of dimension percentages"
    assert all(p >= 0 for p in percentages.values()), "Negative percentages found"
    print(f"✓ Dimension percentages: {[(k, f'{v:.1f}%') for k, v in percentages.items()]}")
    
    # Test 8: Style descriptions
    for dimension in DISCDimension:
        assert dimension in DISCAssessment.STYLE_DESCRIPTIONS, f"Missing description for {dimension}"
        desc = DISCAssessment.STYLE_DESCRIPTIONS[dimension]
        
        required_fields = [
            "name", "description", "core_motivation", "fears",
            "strengths", "challenges", "communication_style",
            "motivation_factors", "stress_indicators", "leadership_style",
            "ideal_environment"
        ]
        
        for field in required_fields:
            assert field in desc, f"Missing {field} in {dimension} description"
    
    print("✓ Style descriptions validation passed")
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! DISC Assessment implementation is working correctly.")
    print("\nSample Result Summary:")
    print(f"Primary Style: {result.primary_style.value} - {DISCAssessment.STYLE_DESCRIPTIONS[result.primary_style]['name']}")
    print(f"Communication Style: {result.communication_style}")
    print(f"Top Strengths: {result.strengths[:3]}")
    print(f"Key Challenges: {result.potential_challenges[:2]}")
    print(f"Leadership Style: {result.leadership_style}")

if __name__ == "__main__":
    test_disc_assessment()
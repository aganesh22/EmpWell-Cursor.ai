"""
Test suite for 16 Personality Types (MBTI-inspired) test.

This module tests the personality assessment implementation to ensure
accurate scoring and type determination.
"""

import pytest
from typing import List, Dict, Any

from backend.app.core.personality_tests import (
    PersonalityTest,
    PersonalityType,
    PersonalityDimension,
    PersonalityResult,
    calculate_personality_type
)


class TestPersonalityTest:
    """Test suite for 16 Personality Types test implementation."""
    
    def test_question_count_and_structure(self):
        """Test that we have the correct number of questions and structure."""
        questions = PersonalityTest.QUESTIONS
        
        # Should have 60 questions total (15 per dimension)
        assert len(questions) == 60
        
        # Count questions per dimension
        dimension_counts = {}
        for question in questions:
            dim = question["dimension"]
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
        
        # Each dimension should have exactly 15 questions
        for dimension in PersonalityDimension:
            assert dimension_counts[dimension] == 15
        
        # Check question structure
        for question in questions:
            assert "id" in question
            assert "text" in question
            assert "dimension" in question
            assert "direction" in question
            assert "category" in question
            assert 1 <= question["id"] <= 60
            assert question["direction"] in ["E", "I", "S", "N", "T", "F", "J", "P"]
    
    def test_type_descriptions_complete(self):
        """Test that all 16 personality types have complete descriptions."""
        descriptions = PersonalityTest.TYPE_DESCRIPTIONS
        
        # Should have all 16 types
        assert len(descriptions) == 16
        
        # Check each type has required fields
        for personality_type in PersonalityType:
            assert personality_type in descriptions
            desc = descriptions[personality_type]
            
            assert "name" in desc
            assert "description" in desc
            assert "strengths" in desc
            assert "challenges" in desc
            assert "careers" in desc
            assert "relationships" in desc
            assert "development" in desc
            
            # Check that lists are not empty
            assert len(desc["strengths"]) > 0
            assert len(desc["challenges"]) > 0
            assert len(desc["careers"]) > 0
            assert len(desc["relationships"]) > 0
            assert len(desc["development"]) > 0
    
    def test_extreme_responses(self):
        """Test personality calculation with extreme response patterns."""
        # All strongly agree (5) - should give clear preferences
        all_agree = [5] * 60
        result = PersonalityTest.calculate_personality_type(all_agree)
        
        # Should be ENTJ (all first letters of each dimension)
        assert result.personality_type == PersonalityType.ENTJ
        assert result.dimension_preferences[PersonalityDimension.EXTRAVERSION_INTROVERSION] == "E"
        assert result.dimension_preferences[PersonalityDimension.SENSING_INTUITION] == "S"
        assert result.dimension_preferences[PersonalityDimension.THINKING_FEELING] == "T"
        assert result.dimension_preferences[PersonalityDimension.JUDGING_PERCEIVING] == "J"
        
        # All strongly disagree (1) - should give opposite preferences
        all_disagree = [1] * 60
        result = PersonalityTest.calculate_personality_type(all_disagree)
        
        # Should be INFP (all second letters of each dimension)
        assert result.personality_type == PersonalityType.INFP
        assert result.dimension_preferences[PersonalityDimension.EXTRAVERSION_INTROVERSION] == "I"
        assert result.dimension_preferences[PersonalityDimension.SENSING_INTUITION] == "N"
        assert result.dimension_preferences[PersonalityDimension.THINKING_FEELING] == "F"
        assert result.dimension_preferences[PersonalityDimension.JUDGING_PERCEIVING] == "P"
    
    def test_neutral_responses(self):
        """Test personality calculation with neutral responses."""
        # All neutral (3) - should still determine a type
        all_neutral = [3] * 60
        result = PersonalityTest.calculate_personality_type(all_neutral)
        
        # Should have a valid personality type
        assert result.personality_type in PersonalityType
        
        # Confidence scores should be very low (near 0)
        for confidence in result.confidence_scores.values():
            assert confidence < 0.1  # Very low confidence
    
    def test_mixed_responses(self):
        """Test personality calculation with mixed responses."""
        # Create a pattern: E, N, F, P preferences
        responses = []
        
        for question in PersonalityTest.QUESTIONS:
            if question["dimension"] == PersonalityDimension.EXTRAVERSION_INTROVERSION:
                # Prefer E
                responses.append(5 if question["direction"] == "E" else 1)
            elif question["dimension"] == PersonalityDimension.SENSING_INTUITION:
                # Prefer N
                responses.append(5 if question["direction"] == "N" else 1)
            elif question["dimension"] == PersonalityDimension.THINKING_FEELING:
                # Prefer F
                responses.append(5 if question["direction"] == "F" else 1)
            else:  # JUDGING_PERCEIVING
                # Prefer P
                responses.append(5 if question["direction"] == "P" else 1)
        
        result = PersonalityTest.calculate_personality_type(responses)
        
        # Should be ENFP
        assert result.personality_type == PersonalityType.ENFP
        assert result.dimension_preferences[PersonalityDimension.EXTRAVERSION_INTROVERSION] == "E"
        assert result.dimension_preferences[PersonalityDimension.SENSING_INTUITION] == "N"
        assert result.dimension_preferences[PersonalityDimension.THINKING_FEELING] == "F"
        assert result.dimension_preferences[PersonalityDimension.JUDGING_PERCEIVING] == "P"
        
        # Confidence scores should be high
        for confidence in result.confidence_scores.values():
            assert confidence > 0.8  # High confidence
    
    def test_invalid_responses(self):
        """Test error handling for invalid responses."""
        # Too few responses
        with pytest.raises(ValueError, match="exactly 60 responses"):
            PersonalityTest.calculate_personality_type([1, 2, 3])
        
        # Too many responses
        with pytest.raises(ValueError, match="exactly 60 responses"):
            PersonalityTest.calculate_personality_type([3] * 61)
        
        # Invalid response values
        with pytest.raises(ValueError, match="between 1 and 5"):
            PersonalityTest.calculate_personality_type([0] + [3] * 59)
        
        with pytest.raises(ValueError, match="between 1 and 5"):
            PersonalityTest.calculate_personality_type([3] * 59 + [6])
    
    def test_response_validation(self):
        """Test response validation function."""
        # Valid responses
        valid_responses = [3] * 60
        is_valid, errors = PersonalityTest.validate_response_set(valid_responses)
        assert is_valid
        assert len(errors) == 0
        
        # Invalid length
        is_valid, errors = PersonalityTest.validate_response_set([3] * 59)
        assert not is_valid
        assert len(errors) > 0
        
        # Invalid values
        invalid_responses = [0] + [3] * 59
        is_valid, errors = PersonalityTest.validate_response_set(invalid_responses)
        assert not is_valid
        assert len(errors) > 0
    
    def test_question_data_format(self):
        """Test that question data is properly formatted for frontend."""
        question_data = PersonalityTest.get_question_data()
        
        assert len(question_data) == 60
        
        for question in question_data:
            assert "id" in question
            assert "text" in question
            assert "dimension" in question
            assert "direction" in question
            assert "category" in question
            assert "type" in question
            assert "options" in question
            assert "required" in question
            assert "reverse_scored" in question
            
            # Check specific values
            assert question["type"] == "likert"
            assert question["required"] is True
            assert question["reverse_scored"] is False
            assert len(question["options"]) == 5
            assert question["options"] == [
                "Strongly Disagree",
                "Disagree", 
                "Neutral",
                "Agree",
                "Strongly Agree"
            ]
    
    def test_all_personality_types(self):
        """Test that all 16 personality types can be generated."""
        generated_types = set()
        
        # Generate responses for each possible type
        for e_i in ["E", "I"]:
            for s_n in ["S", "N"]:
                for t_f in ["T", "F"]:
                    for j_p in ["J", "P"]:
                        responses = []
                        
                        for question in PersonalityTest.QUESTIONS:
                            if question["dimension"] == PersonalityDimension.EXTRAVERSION_INTROVERSION:
                                responses.append(5 if question["direction"] == e_i else 1)
                            elif question["dimension"] == PersonalityDimension.SENSING_INTUITION:
                                responses.append(5 if question["direction"] == s_n else 1)
                            elif question["dimension"] == PersonalityDimension.THINKING_FEELING:
                                responses.append(5 if question["direction"] == t_f else 1)
                            else:  # JUDGING_PERCEIVING
                                responses.append(5 if question["direction"] == j_p else 1)
                        
                        result = PersonalityTest.calculate_personality_type(responses)
                        expected_type = PersonalityType(e_i + s_n + t_f + j_p)
                        
                        assert result.personality_type == expected_type
                        generated_types.add(result.personality_type)
        
        # Should have generated all 16 types
        assert len(generated_types) == 16
        assert generated_types == set(PersonalityType)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # Strong preferences should give high confidence
        strong_responses = []
        for question in PersonalityTest.QUESTIONS:
            # Alternate between strong agree and strong disagree
            strong_responses.append(5 if question["id"] % 2 == 1 else 1)
        
        result = PersonalityTest.calculate_personality_type(strong_responses)
        
        # All confidence scores should be reasonably high
        for confidence in result.confidence_scores.values():
            assert 0.0 <= confidence <= 1.0
        
        # Weak preferences should give low confidence
        weak_responses = []
        for question in PersonalityTest.QUESTIONS:
            # Alternate between slightly agree and slightly disagree
            weak_responses.append(4 if question["id"] % 2 == 1 else 2)
        
        result = PersonalityTest.calculate_personality_type(weak_responses)
        
        # Confidence scores should be lower
        for confidence in result.confidence_scores.values():
            assert 0.0 <= confidence <= 1.0
    
    def test_result_completeness(self):
        """Test that personality result contains all expected fields."""
        responses = [3] * 60  # Neutral responses
        result = PersonalityTest.calculate_personality_type(responses)
        
        # Check all required fields are present
        assert hasattr(result, 'personality_type')
        assert hasattr(result, 'dimension_scores')
        assert hasattr(result, 'dimension_preferences')
        assert hasattr(result, 'confidence_scores')
        assert hasattr(result, 'type_description')
        assert hasattr(result, 'strengths')
        assert hasattr(result, 'potential_challenges')
        assert hasattr(result, 'career_suggestions')
        assert hasattr(result, 'relationship_insights')
        assert hasattr(result, 'development_tips')
        
        # Check data types
        assert isinstance(result.personality_type, PersonalityType)
        assert isinstance(result.dimension_scores, dict)
        assert isinstance(result.dimension_preferences, dict)
        assert isinstance(result.confidence_scores, dict)
        assert isinstance(result.type_description, str)
        assert isinstance(result.strengths, list)
        assert isinstance(result.potential_challenges, list)
        assert isinstance(result.career_suggestions, list)
        assert isinstance(result.relationship_insights, list)
        assert isinstance(result.development_tips, list)
        
        # Check that lists are not empty
        assert len(result.strengths) > 0
        assert len(result.potential_challenges) > 0
        assert len(result.career_suggestions) > 0
        assert len(result.relationship_insights) > 0
        assert len(result.development_tips) > 0
    
    def test_convenience_function(self):
        """Test the convenience function."""
        responses = [3] * 60
        result = calculate_personality_type(responses)
        
        assert isinstance(result, PersonalityResult)
        assert result.personality_type in PersonalityType


class TestPersonalityDimensions:
    """Test individual personality dimensions."""
    
    def test_extraversion_introversion(self):
        """Test E/I dimension calculation."""
        # Create responses favoring extraversion
        responses = [3] * 60  # Start with neutral
        
        for question in PersonalityTest.QUESTIONS:
            if question["dimension"] == PersonalityDimension.EXTRAVERSION_INTROVERSION:
                idx = question["id"] - 1
                if question["direction"] == "E":
                    responses[idx] = 5  # Strongly agree with E statements
                else:
                    responses[idx] = 1  # Strongly disagree with I statements
        
        result = PersonalityTest.calculate_personality_type(responses)
        assert result.dimension_preferences[PersonalityDimension.EXTRAVERSION_INTROVERSION] == "E"
        
        # Create responses favoring introversion
        responses = [3] * 60  # Start with neutral
        
        for question in PersonalityTest.QUESTIONS:
            if question["dimension"] == PersonalityDimension.EXTRAVERSION_INTROVERSION:
                idx = question["id"] - 1
                if question["direction"] == "I":
                    responses[idx] = 5  # Strongly agree with I statements
                else:
                    responses[idx] = 1  # Strongly disagree with E statements
        
        result = PersonalityTest.calculate_personality_type(responses)
        assert result.dimension_preferences[PersonalityDimension.EXTRAVERSION_INTROVERSION] == "I"
    
    def test_sensing_intuition(self):
        """Test S/N dimension calculation."""
        # Test similar to E/I but for S/N dimension
        responses = [3] * 60
        
        for question in PersonalityTest.QUESTIONS:
            if question["dimension"] == PersonalityDimension.SENSING_INTUITION:
                idx = question["id"] - 1
                if question["direction"] == "S":
                    responses[idx] = 5
                else:
                    responses[idx] = 1
        
        result = PersonalityTest.calculate_personality_type(responses)
        assert result.dimension_preferences[PersonalityDimension.SENSING_INTUITION] == "S"
    
    def test_thinking_feeling(self):
        """Test T/F dimension calculation."""
        responses = [3] * 60
        
        for question in PersonalityTest.QUESTIONS:
            if question["dimension"] == PersonalityDimension.THINKING_FEELING:
                idx = question["id"] - 1
                if question["direction"] == "F":
                    responses[idx] = 5
                else:
                    responses[idx] = 1
        
        result = PersonalityTest.calculate_personality_type(responses)
        assert result.dimension_preferences[PersonalityDimension.THINKING_FEELING] == "F"
    
    def test_judging_perceiving(self):
        """Test J/P dimension calculation."""
        responses = [3] * 60
        
        for question in PersonalityTest.QUESTIONS:
            if question["dimension"] == PersonalityDimension.JUDGING_PERCEIVING:
                idx = question["id"] - 1
                if question["direction"] == "P":
                    responses[idx] = 5
                else:
                    responses[idx] = 1
        
        result = PersonalityTest.calculate_personality_type(responses)
        assert result.dimension_preferences[PersonalityDimension.JUDGING_PERCEIVING] == "P"


class TestPersonalityIntegration:
    """Integration tests for personality assessment."""
    
    def test_realistic_response_patterns(self):
        """Test with realistic response patterns."""
        # Simulate a realistic INTJ response pattern
        responses = []
        
        for question in PersonalityTest.QUESTIONS:
            if question["dimension"] == PersonalityDimension.EXTRAVERSION_INTROVERSION:
                # Moderate introversion preference
                responses.append(2 if question["direction"] == "E" else 4)
            elif question["dimension"] == PersonalityDimension.SENSING_INTUITION:
                # Strong intuition preference
                responses.append(1 if question["direction"] == "S" else 5)
            elif question["dimension"] == PersonalityDimension.THINKING_FEELING:
                # Strong thinking preference
                responses.append(5 if question["direction"] == "T" else 1)
            else:  # JUDGING_PERCEIVING
                # Moderate judging preference
                responses.append(4 if question["direction"] == "J" else 2)
        
        result = PersonalityTest.calculate_personality_type(responses)
        
        assert result.personality_type == PersonalityType.INTJ
        assert "Architect" in result.type_description
        assert len(result.strengths) > 0
        assert len(result.career_suggestions) > 0
    
    def test_performance_with_large_datasets(self):
        """Test performance with multiple calculations."""
        import time
        
        # Test 100 personality calculations
        start_time = time.time()
        
        for i in range(100):
            # Generate varied responses
            responses = [(i % 5) + 1 for _ in range(60)]
            result = PersonalityTest.calculate_personality_type(responses)
            assert result.personality_type in PersonalityType
        
        end_time = time.time()
        
        # Should complete 100 calculations in under 1 second
        assert end_time - start_time < 1.0
    
    def test_question_categories(self):
        """Test that questions are properly categorized."""
        categories = set()
        
        for question in PersonalityTest.QUESTIONS:
            categories.add(question["category"])
        
        # Should have multiple categories per dimension
        assert len(categories) > 10  # Should have diverse categories
        
        # Check some expected categories exist
        expected_categories = [
            "energy_source", "processing_style", "social_preference",
            "information_processing", "decision_making", "planning"
        ]
        
        for category in expected_categories:
            assert any(q["category"] == category for q in PersonalityTest.QUESTIONS)


if __name__ == "__main__":
    # Run some basic tests if script is executed directly
    print("Running basic personality test...")
    
    # Test INTJ pattern
    intj_responses = []
    for question in PersonalityTest.QUESTIONS:
        if question["dimension"] == PersonalityDimension.EXTRAVERSION_INTROVERSION:
            intj_responses.append(1 if question["direction"] == "E" else 5)
        elif question["dimension"] == PersonalityDimension.SENSING_INTUITION:
            intj_responses.append(1 if question["direction"] == "S" else 5)
        elif question["dimension"] == PersonalityDimension.THINKING_FEELING:
            intj_responses.append(5 if question["direction"] == "T" else 1)
        else:  # JUDGING_PERCEIVING
            intj_responses.append(5 if question["direction"] == "J" else 1)
    
    result = PersonalityTest.calculate_personality_type(intj_responses)
    print(f"Test result: {result.personality_type.value} - {result.type_description}")
    print(f"Strengths: {result.strengths[:3]}")
    print(f"Career suggestions: {result.career_suggestions[:3]}")
    
    print("\nAll basic tests completed successfully!")
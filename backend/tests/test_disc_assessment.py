"""
Tests for DISC Assessment functionality.

This module contains comprehensive tests for the DISC assessment implementation,
including scoring algorithm, API endpoints, and data validation.
"""

import pytest
from typing import List
from unittest.mock import Mock, patch

from backend.app.core.disc_assessment import (
    DISCAssessment, 
    DISCDimension, 
    DISCProfile,
    DISCResult,
    calculate_disc_profile
)


class TestDISCAssessment:
    """Test suite for DISC Assessment core functionality."""
    
    def test_question_count(self):
        """Test that DISC assessment has exactly 28 questions."""
        assert len(DISCAssessment.QUESTIONS) == 28
        
    def test_question_structure(self):
        """Test that each question has the correct structure."""
        for i, question in enumerate(DISCAssessment.QUESTIONS):
            assert question["id"] == i + 1
            assert "instruction" in question
            assert "words" in question
            assert len(question["words"]) == 4
            
            for word in question["words"]:
                assert "text" in word
                assert "dimension" in word
                assert "weight" in word
                assert isinstance(word["dimension"], DISCDimension)
                assert isinstance(word["weight"], (int, float))
                assert 0 <= word["weight"] <= 1.0
    
    def test_dimension_coverage(self):
        """Test that all DISC dimensions are represented in questions."""
        dimensions_found = set()
        
        for question in DISCAssessment.QUESTIONS:
            for word in question["words"]:
                dimensions_found.add(word["dimension"])
        
        assert dimensions_found == set(DISCDimension)
    
    def test_get_question_data(self):
        """Test question data formatting for frontend."""
        questions = DISCAssessment.get_question_data()
        
        assert len(questions) == 28
        
        for question in questions:
            assert "id" in question
            assert "instruction" in question
            assert "words" in question
            assert "type" in question
            assert "required" in question
            assert question["type"] == "forced_choice"
            assert question["required"] is True
            assert len(question["words"]) == 4
            
            for word in question["words"]:
                assert "text" in word
                assert "index" in word
                assert isinstance(word["index"], int)
                assert 0 <= word["index"] <= 3
    
    def test_validate_response_set_valid(self):
        """Test validation of valid response sets."""
        most_responses = [0, 1, 2, 3] * 7  # 28 responses
        least_responses = [3, 2, 1, 0] * 7  # 28 responses
        
        is_valid, errors = DISCAssessment.validate_response_set(
            most_responses, least_responses
        )
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_response_set_wrong_length(self):
        """Test validation with wrong number of responses."""
        most_responses = [0, 1, 2]  # Too few
        least_responses = [3, 2, 1, 0] * 7  # Correct length
        
        is_valid, errors = DISCAssessment.validate_response_set(
            most_responses, least_responses
        )
        
        assert is_valid is False
        assert len(errors) > 0
        assert "Expected 28 most responses" in errors[0]
    
    def test_validate_response_set_invalid_values(self):
        """Test validation with invalid response values."""
        most_responses = [0, 1, 2, 4] * 7  # Contains invalid value 4
        least_responses = [3, 2, 1, 0] * 7
        
        is_valid, errors = DISCAssessment.validate_response_set(
            most_responses, least_responses
        )
        
        assert is_valid is False
        assert any("must be between 0 and 3" in error for error in errors)
    
    def test_validate_response_set_same_values(self):
        """Test validation when most and least responses are the same."""
        most_responses = [0, 1, 2, 0] * 7  # Same as least in some positions
        least_responses = [0, 2, 1, 0] * 7
        
        is_valid, errors = DISCAssessment.validate_response_set(
            most_responses, least_responses
        )
        
        assert is_valid is False
        assert any("cannot be the same" in error for error in errors)


class TestDISCScoring:
    """Test suite for DISC scoring algorithm."""
    
    def test_calculate_disc_profile_basic(self):
        """Test basic DISC profile calculation."""
        # Create responses that favor Dominance
        most_responses = []
        least_responses = []
        
        for i in range(28):
            question = DISCAssessment.QUESTIONS[i]
            
            # Find Dominance word if available, otherwise first word
            dominance_idx = None
            for j, word in enumerate(question["words"]):
                if word["dimension"] == DISCDimension.DOMINANCE:
                    dominance_idx = j
                    break
            
            most_responses.append(dominance_idx if dominance_idx is not None else 0)
            
            # Find non-Dominance word for least
            least_idx = 0
            for j, word in enumerate(question["words"]):
                if word["dimension"] != DISCDimension.DOMINANCE:
                    least_idx = j
                    break
            
            least_responses.append(least_idx)
        
        result = DISCAssessment.calculate_disc_profile(most_responses, least_responses)
        
        assert isinstance(result, DISCResult)
        assert result.primary_style == DISCDimension.DOMINANCE
        assert result.dimension_percentages[DISCDimension.DOMINANCE] > 25.0
    
    def test_calculate_disc_profile_invalid_length(self):
        """Test profile calculation with invalid response length."""
        most_responses = [0, 1, 2]  # Too few
        least_responses = [3, 2, 1]  # Too few
        
        with pytest.raises(ValueError, match="requires exactly 28"):
            DISCAssessment.calculate_disc_profile(most_responses, least_responses)
    
    def test_calculate_disc_profile_invalid_values(self):
        """Test profile calculation with invalid response values."""
        most_responses = [4] * 28  # Invalid values
        least_responses = [0] * 28
        
        with pytest.raises(ValueError, match="must be between 0 and 3"):
            DISCAssessment.calculate_disc_profile(most_responses, least_responses)
    
    def test_dimension_percentages_sum(self):
        """Test that dimension percentages are properly calculated."""
        most_responses = [0, 1, 2, 3] * 7
        least_responses = [3, 2, 1, 0] * 7
        
        result = DISCAssessment.calculate_disc_profile(most_responses, least_responses)
        
        # Check that all percentages are non-negative
        for percentage in result.dimension_percentages.values():
            assert percentage >= 0
        
        # Check that we have all dimensions
        assert len(result.dimension_percentages) == 4
        assert set(result.dimension_percentages.keys()) == set(DISCDimension)
    
    def test_profile_type_determination(self):
        """Test profile type determination logic."""
        most_responses = [0, 1, 2, 3] * 7
        least_responses = [3, 2, 1, 0] * 7
        
        result = DISCAssessment.calculate_disc_profile(most_responses, least_responses)
        
        assert isinstance(result.profile_type, DISCProfile)
        assert result.primary_style in DISCDimension
        
        # If secondary style exists, it should be different from primary
        if result.secondary_style:
            assert result.secondary_style != result.primary_style
    
    def test_intensity_level_calculation(self):
        """Test intensity level calculation."""
        most_responses = [0, 1, 2, 3] * 7
        least_responses = [3, 2, 1, 0] * 7
        
        result = DISCAssessment.calculate_disc_profile(most_responses, least_responses)
        
        assert result.intensity_level in ["High", "Moderate", "Low"]
    
    def test_comprehensive_result_structure(self):
        """Test that result contains all expected fields."""
        most_responses = [0, 1, 2, 3] * 7
        least_responses = [3, 2, 1, 0] * 7
        
        result = DISCAssessment.calculate_disc_profile(most_responses, least_responses)
        
        # Check basic profile info
        assert hasattr(result, 'dimension_scores')
        assert hasattr(result, 'dimension_percentages')
        assert hasattr(result, 'primary_style')
        assert hasattr(result, 'secondary_style')
        assert hasattr(result, 'profile_type')
        assert hasattr(result, 'intensity_level')
        
        # Check detailed analysis
        assert hasattr(result, 'strengths')
        assert hasattr(result, 'potential_challenges')
        assert hasattr(result, 'communication_style')
        assert hasattr(result, 'motivation_factors')
        assert hasattr(result, 'stress_indicators')
        assert hasattr(result, 'leadership_style')
        assert hasattr(result, 'team_contribution')
        assert hasattr(result, 'development_areas')
        
        # Check workplace insights
        assert hasattr(result, 'ideal_environment')
        assert hasattr(result, 'decision_making_style')
        assert hasattr(result, 'conflict_resolution')
        assert hasattr(result, 'change_adaptation')
        
        # Check that lists are properly limited
        assert len(result.strengths) <= 8
        assert len(result.potential_challenges) <= 6
        assert len(result.development_areas) <= 6


class TestDISCStyleDescriptions:
    """Test suite for DISC style descriptions."""
    
    def test_all_dimensions_have_descriptions(self):
        """Test that all DISC dimensions have complete descriptions."""
        for dimension in DISCDimension:
            assert dimension in DISCAssessment.STYLE_DESCRIPTIONS
            
            desc = DISCAssessment.STYLE_DESCRIPTIONS[dimension]
            
            # Check required fields
            required_fields = [
                "name", "description", "core_motivation", "fears",
                "strengths", "challenges", "communication_style",
                "motivation_factors", "stress_indicators", "leadership_style",
                "ideal_environment"
            ]
            
            for field in required_fields:
                assert field in desc, f"Missing {field} in {dimension} description"
    
    def test_strengths_and_challenges_are_lists(self):
        """Test that strengths and challenges are properly formatted lists."""
        for dimension in DISCDimension:
            desc = DISCAssessment.STYLE_DESCRIPTIONS[dimension]
            
            assert isinstance(desc["strengths"], list)
            assert isinstance(desc["challenges"], list)
            assert isinstance(desc["motivation_factors"], list)
            assert isinstance(desc["stress_indicators"], list)
            assert isinstance(desc["ideal_environment"], list)
            
            # Check that lists are not empty
            assert len(desc["strengths"]) > 0
            assert len(desc["challenges"]) > 0
            assert len(desc["motivation_factors"]) > 0
            assert len(desc["stress_indicators"]) > 0
            assert len(desc["ideal_environment"]) > 0


class TestDISCHelperMethods:
    """Test suite for DISC helper methods."""
    
    def test_get_decision_making_style(self):
        """Test decision making style generation."""
        for dimension in DISCDimension:
            style = DISCAssessment._get_decision_making_style(dimension, None)
            assert isinstance(style, str)
            assert len(style) > 0
    
    def test_get_conflict_resolution_style(self):
        """Test conflict resolution style generation."""
        for dimension in DISCDimension:
            style = DISCAssessment._get_conflict_resolution_style(dimension, None)
            assert isinstance(style, str)
            assert len(style) > 0
    
    def test_get_change_adaptation_style(self):
        """Test change adaptation style generation."""
        for dimension in DISCDimension:
            style = DISCAssessment._get_change_adaptation_style(dimension, None)
            assert isinstance(style, str)
            assert len(style) > 0
    
    def test_get_team_contribution(self):
        """Test team contribution generation."""
        for dimension in DISCDimension:
            contribution = DISCAssessment._get_team_contribution(dimension, None)
            assert isinstance(contribution, str)
            assert len(contribution) > 0
            
            # Test with secondary dimension
            for secondary in DISCDimension:
                if secondary != dimension:
                    contribution_with_secondary = DISCAssessment._get_team_contribution(
                        dimension, secondary
                    )
                    assert isinstance(contribution_with_secondary, str)
                    assert len(contribution_with_secondary) > len(contribution)
    
    def test_get_development_areas(self):
        """Test development areas generation."""
        for dimension in DISCDimension:
            areas = DISCAssessment._get_development_areas(dimension, None)
            assert isinstance(areas, list)
            assert len(areas) > 0
            assert len(areas) <= 6  # Should be limited to 6
            
            # Test with secondary dimension
            for secondary in DISCDimension:
                if secondary != dimension:
                    areas_with_secondary = DISCAssessment._get_development_areas(
                        dimension, secondary
                    )
                    assert isinstance(areas_with_secondary, list)
                    assert len(areas_with_secondary) <= 6


class TestConvenienceFunction:
    """Test suite for the convenience function."""
    
    def test_calculate_disc_profile_function(self):
        """Test the standalone calculate_disc_profile function."""
        most_responses = [0, 1, 2, 3] * 7
        least_responses = [3, 2, 1, 0] * 7
        
        result = calculate_disc_profile(most_responses, least_responses)
        
        assert isinstance(result, DISCResult)
        assert result.primary_style in DISCDimension


if __name__ == "__main__":
    pytest.main([__file__])
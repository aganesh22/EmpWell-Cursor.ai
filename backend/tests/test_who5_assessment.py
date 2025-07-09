"""
Tests for WHO-5 Wellbeing Index Assessment functionality.

This module contains comprehensive tests for the WHO-5 assessment implementation,
including scoring algorithm, API endpoints, and clinical interpretation.
"""

import pytest
from typing import List

from backend.app.core.who5_assessment import (
    WHO5Assessment, 
    WHO5ScoreLevel, 
    WHO5Result,
    calculate_who5_score
)


class TestWHO5Assessment:
    """Test suite for WHO-5 Assessment core functionality."""
    
    def test_question_count(self):
        """Test that WHO-5 assessment has exactly 5 questions."""
        assert len(WHO5Assessment.QUESTIONS) == 5
        
    def test_question_structure(self):
        """Test that each question has the correct structure."""
        for i, question in enumerate(WHO5Assessment.QUESTIONS):
            assert question["id"] == i + 1
            assert "text" in question
            assert "timeframe" in question
            assert "area" in question
            assert question["timeframe"] == "Over the last two weeks"
    
    def test_response_scale(self):
        """Test response scale structure."""
        assert len(WHO5Assessment.RESPONSE_SCALE) == 6  # 0-5 scale
        
        for i, response in enumerate(WHO5Assessment.RESPONSE_SCALE):
            assert response["value"] == i
            assert "label" in response
            assert "description" in response
    
    def test_score_thresholds(self):
        """Test score threshold definitions."""
        assert len(WHO5Assessment.SCORE_THRESHOLDS) == 5
        
        # Check that thresholds cover the full range
        all_ranges = []
        for level, (min_score, max_score) in WHO5Assessment.SCORE_THRESHOLDS.items():
            all_ranges.extend(range(min_score, max_score + 1))
        
        # Should cover 0-100
        assert min(all_ranges) == 0
        assert max(all_ranges) == 100
    
    def test_get_question_data(self):
        """Test question data formatting for frontend."""
        questions = WHO5Assessment.get_question_data()
        
        assert len(questions) == 5
        
        for question in questions:
            assert "id" in question
            assert "text" in question
            assert "timeframe" in question
            assert "area" in question
            assert "response_scale" in question
            assert "type" in question
            assert "required" in question
            assert "min_value" in question
            assert "max_value" in question
            
            assert question["type"] == "likert"
            assert question["required"] is True
            assert question["min_value"] == 0
            assert question["max_value"] == 5
            assert len(question["response_scale"]) == 6
    
    def test_validate_responses_valid(self):
        """Test validation of valid responses."""
        valid_responses = [0, 1, 2, 3, 4]
        
        is_valid, errors = WHO5Assessment.validate_responses(valid_responses)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_responses_wrong_length(self):
        """Test validation with wrong number of responses."""
        invalid_responses = [0, 1, 2]  # Too few
        
        is_valid, errors = WHO5Assessment.validate_responses(invalid_responses)
        
        assert is_valid is False
        assert len(errors) > 0
        assert "Expected 5 responses" in errors[0]
    
    def test_validate_responses_invalid_values(self):
        """Test validation with invalid response values."""
        invalid_responses = [0, 1, 2, 3, 6]  # 6 is out of range
        
        is_valid, errors = WHO5Assessment.validate_responses(invalid_responses)
        
        assert is_valid is False
        assert len(errors) > 0
        assert "must be between 0 and 5" in errors[0]
    
    def test_validate_responses_non_integer(self):
        """Test validation with non-integer responses."""
        invalid_responses = [0, 1, 2, 3, "4"]  # String instead of int
        
        is_valid, errors = WHO5Assessment.validate_responses(invalid_responses)
        
        assert is_valid is False
        assert len(errors) > 0
        assert "must be an integer" in errors[0]


class TestWHO5Scoring:
    """Test suite for WHO-5 scoring algorithm."""
    
    def test_calculate_who5_score_basic(self):
        """Test basic WHO-5 score calculation."""
        responses = [3, 2, 4, 1, 5]  # Raw score = 15
        
        result = WHO5Assessment.calculate_who5_score(responses)
        
        assert isinstance(result, WHO5Result)
        assert result.raw_score == 15
        assert result.percentage_score == 60  # 15 * 4 = 60
        assert result.score_level == WHO5ScoreLevel.AVERAGE
    
    def test_calculate_who5_score_minimum(self):
        """Test WHO-5 score calculation with minimum values."""
        responses = [0, 0, 0, 0, 0]  # Raw score = 0
        
        result = WHO5Assessment.calculate_who5_score(responses)
        
        assert result.raw_score == 0
        assert result.percentage_score == 0  # 0 * 4 = 0
        assert result.score_level == WHO5ScoreLevel.POOR
        assert result.follow_up_needed is True
    
    def test_calculate_who5_score_maximum(self):
        """Test WHO-5 score calculation with maximum values."""
        responses = [5, 5, 5, 5, 5]  # Raw score = 25
        
        result = WHO5Assessment.calculate_who5_score(responses)
        
        assert result.raw_score == 25
        assert result.percentage_score == 100  # 25 * 4 = 100
        assert result.score_level == WHO5ScoreLevel.EXCELLENT
        assert result.follow_up_needed is False
    
    def test_calculate_who5_score_depression_threshold(self):
        """Test WHO-5 score at depression screening threshold."""
        # Score of 50% (raw score 12.5, but we'll use 12 and 13)
        responses_below = [3, 2, 2, 2, 3]  # Raw score = 12, percentage = 48
        responses_above = [3, 3, 2, 2, 3]  # Raw score = 13, percentage = 52
        
        result_below = WHO5Assessment.calculate_who5_score(responses_below)
        result_above = WHO5Assessment.calculate_who5_score(responses_above)
        
        assert result_below.percentage_score == 48
        assert result_below.follow_up_needed is True
        assert "depression screening" in result_below.depression_screening.lower()
        
        assert result_above.percentage_score == 52
        assert result_above.follow_up_needed is False
    
    def test_calculate_who5_score_invalid_length(self):
        """Test score calculation with invalid response length."""
        responses = [0, 1, 2]  # Too few
        
        with pytest.raises(ValueError, match="requires exactly 5 responses"):
            WHO5Assessment.calculate_who5_score(responses)
    
    def test_calculate_who5_score_invalid_values(self):
        """Test score calculation with invalid response values."""
        responses = [0, 1, 2, 3, 6]  # 6 is out of range
        
        with pytest.raises(ValueError, match="must be integers between 0 and 5"):
            WHO5Assessment.calculate_who5_score(responses)
    
    def test_score_level_determination(self):
        """Test score level determination for different percentage scores."""
        test_cases = [
            (0, WHO5ScoreLevel.POOR),
            (28, WHO5ScoreLevel.POOR),
            (29, WHO5ScoreLevel.BELOW_AVERAGE),
            (50, WHO5ScoreLevel.BELOW_AVERAGE),
            (51, WHO5ScoreLevel.AVERAGE),
            (68, WHO5ScoreLevel.AVERAGE),
            (69, WHO5ScoreLevel.GOOD),
            (84, WHO5ScoreLevel.GOOD),
            (85, WHO5ScoreLevel.EXCELLENT),
            (100, WHO5ScoreLevel.EXCELLENT)
        ]
        
        for percentage, expected_level in test_cases:
            level = WHO5Assessment._get_score_level(percentage)
            assert level == expected_level, f"Score {percentage} should be {expected_level}, got {level}"
    
    def test_comprehensive_result_structure(self):
        """Test that result contains all expected fields."""
        responses = [3, 2, 4, 1, 5]
        
        result = WHO5Assessment.calculate_who5_score(responses)
        
        # Check basic score info
        assert hasattr(result, 'raw_score')
        assert hasattr(result, 'percentage_score')
        assert hasattr(result, 'score_level')
        
        # Check detailed interpretation
        assert hasattr(result, 'interpretation')
        assert hasattr(result, 'recommendations')
        assert hasattr(result, 'risk_indicators')
        assert hasattr(result, 'strengths')
        
        # Check clinical insights
        assert hasattr(result, 'depression_screening')
        assert hasattr(result, 'wellbeing_status')
        assert hasattr(result, 'follow_up_needed')
        
        # Check individual question analysis
        assert hasattr(result, 'question_scores')
        assert hasattr(result, 'lowest_scoring_areas')
        assert hasattr(result, 'highest_scoring_areas')
        
        # Check that all fields have appropriate types
        assert isinstance(result.raw_score, int)
        assert isinstance(result.percentage_score, int)
        assert isinstance(result.score_level, WHO5ScoreLevel)
        assert isinstance(result.interpretation, str)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.risk_indicators, list)
        assert isinstance(result.strengths, list)
        assert isinstance(result.depression_screening, str)
        assert isinstance(result.wellbeing_status, str)
        assert isinstance(result.follow_up_needed, bool)
        assert isinstance(result.question_scores, dict)
        assert isinstance(result.lowest_scoring_areas, list)
        assert isinstance(result.highest_scoring_areas, list)
    
    def test_question_scores_mapping(self):
        """Test that question scores are correctly mapped."""
        responses = [1, 2, 3, 4, 5]
        
        result = WHO5Assessment.calculate_who5_score(responses)
        
        expected_scores = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
        assert result.question_scores == expected_scores


class TestWHO5Interpretation:
    """Test suite for WHO-5 interpretation logic."""
    
    def test_interpretation_generation(self):
        """Test that interpretations are generated for all score levels."""
        test_scores = [0, 30, 60, 75, 90]  # One from each level
        
        for score in test_scores:
            level = WHO5Assessment._get_score_level(score)
            interpretation = WHO5Assessment._get_interpretation(score, level)
            
            assert isinstance(interpretation, str)
            assert len(interpretation) > 0
            assert str(score) in interpretation
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated appropriately."""
        # Test different score levels
        test_cases = [
            ([0, 0, 0, 0, 0], "professional"),  # Should recommend professional help
            ([2, 2, 2, 2, 2], "support"),      # Should recommend support
            ([3, 3, 3, 3, 3], "continue"),     # Should recommend continuing practices
            ([5, 5, 5, 5, 5], "maintain")      # Should recommend maintaining
        ]
        
        for responses, expected_keyword in test_cases:
            result = WHO5Assessment.calculate_who5_score(responses)
            recommendations_text = " ".join(result.recommendations).lower()
            
            assert len(result.recommendations) > 0
            # Check that appropriate recommendations are included
            assert any(expected_keyword in rec.lower() for rec in result.recommendations)
    
    def test_risk_indicators_identification(self):
        """Test risk indicator identification."""
        # High risk case
        high_risk_responses = [0, 0, 0, 0, 0]
        result = WHO5Assessment.calculate_who5_score(high_risk_responses)
        
        assert len(result.risk_indicators) > 0
        assert result.follow_up_needed is True
        
        # Low risk case
        low_risk_responses = [4, 4, 4, 4, 4]
        result = WHO5Assessment.calculate_who5_score(low_risk_responses)
        
        assert result.follow_up_needed is False
    
    def test_strengths_identification(self):
        """Test strength identification."""
        # Case with clear strengths
        responses_with_strengths = [5, 4, 3, 2, 1]
        result = WHO5Assessment.calculate_who5_score(responses_with_strengths)
        
        assert len(result.strengths) > 0
        
        # Case with no clear strengths
        low_responses = [1, 1, 1, 1, 1]
        result = WHO5Assessment.calculate_who5_score(low_responses)
        
        # Should still identify relative strengths
        assert len(result.strengths) > 0
    
    def test_area_analysis(self):
        """Test lowest and highest scoring area identification."""
        responses = [1, 5, 2, 4, 3]  # mood=1(low), relaxation=5(high), energy=2, sleep=4, interest=3
        
        result = WHO5Assessment.calculate_who5_score(responses)
        
        # Should identify mood as lowest scoring area
        assert len(result.lowest_scoring_areas) > 0
        assert any("mood" in area.lower() for area in result.lowest_scoring_areas)
        
        # Should identify relaxation as highest scoring area
        assert len(result.highest_scoring_areas) > 0
        assert any("relaxation" in area.lower() for area in result.highest_scoring_areas)


class TestWHO5Clinical:
    """Test suite for WHO-5 clinical features."""
    
    def test_depression_screening_recommendations(self):
        """Test depression screening recommendations."""
        # Score above threshold
        above_threshold = [3, 3, 3, 3, 3]  # 60%
        result = WHO5Assessment.calculate_who5_score(above_threshold)
        
        assert result.follow_up_needed is False
        assert "does not indicate immediate need" in result.depression_screening
        
        # Score at/below threshold
        below_threshold = [2, 2, 2, 2, 2]  # 40%
        result = WHO5Assessment.calculate_who5_score(below_threshold)
        
        assert result.follow_up_needed is True
        assert "screening is recommended" in result.depression_screening
    
    def test_wellbeing_status_classification(self):
        """Test wellbeing status classification."""
        test_cases = [
            ([0, 0, 0, 0, 0], "poor"),
            ([2, 2, 2, 2, 2], "below average"),
            ([3, 3, 3, 3, 3], "average"),
            ([4, 4, 4, 4, 4], "good"),
            ([5, 5, 5, 5, 5], "excellent")
        ]
        
        for responses, expected_status in test_cases:
            result = WHO5Assessment.calculate_who5_score(responses)
            status = result.wellbeing_status.lower()
            
            assert expected_status in status
    
    def test_clinical_thresholds(self):
        """Test clinical threshold constants."""
        assert WHO5Assessment.DEPRESSION_SCREENING_THRESHOLD == 50
        
        # Test that threshold is correctly applied
        threshold_responses = [2, 2, 2, 2, 3]  # Should be exactly 44%
        result = WHO5Assessment.calculate_who5_score(threshold_responses)
        
        assert result.percentage_score < WHO5Assessment.DEPRESSION_SCREENING_THRESHOLD
        assert result.follow_up_needed is True


class TestConvenienceFunction:
    """Test suite for the convenience function."""
    
    def test_calculate_who5_score_function(self):
        """Test the standalone calculate_who5_score function."""
        responses = [3, 2, 4, 1, 5]
        
        result = calculate_who5_score(responses)
        
        assert isinstance(result, WHO5Result)
        assert result.raw_score == 15
        assert result.percentage_score == 60


class TestWHO5EdgeCases:
    """Test suite for WHO-5 edge cases."""
    
    def test_all_same_responses(self):
        """Test with all identical responses."""
        for value in range(6):  # 0-5
            responses = [value] * 5
            result = WHO5Assessment.calculate_who5_score(responses)
            
            expected_raw = value * 5
            expected_percentage = expected_raw * 4
            
            assert result.raw_score == expected_raw
            assert result.percentage_score == expected_percentage
    
    def test_mixed_extreme_responses(self):
        """Test with mixed extreme responses."""
        responses = [0, 5, 0, 5, 0]  # Mix of lowest and highest
        
        result = WHO5Assessment.calculate_who5_score(responses)
        
        assert result.raw_score == 10  # 0+5+0+5+0
        assert result.percentage_score == 40  # 10*4
        assert result.score_level == WHO5ScoreLevel.BELOW_AVERAGE
    
    def test_boundary_scores(self):
        """Test scores at boundaries between levels."""
        boundary_cases = [
            (7, 28),   # 7*4 = 28 (boundary between POOR and BELOW_AVERAGE)
            (12, 48),  # 12*4 = 48 (near depression threshold)
            (13, 52),  # 13*4 = 52 (just above depression threshold)
            (17, 68),  # 17*4 = 68 (boundary between AVERAGE and GOOD)
            (21, 84)   # 21*4 = 84 (boundary between GOOD and EXCELLENT)
        ]
        
        for raw_score, expected_percentage in boundary_cases:
            # Create responses that sum to raw_score
            responses = [raw_score // 5] * 4 + [raw_score % 5 + raw_score // 5]
            if sum(responses) != raw_score:
                # Adjust if needed
                responses = [raw_score // 5] * 5
                responses[0] += raw_score % 5
            
            result = WHO5Assessment.calculate_who5_score(responses)
            assert result.percentage_score == expected_percentage


if __name__ == "__main__":
    pytest.main([__file__])
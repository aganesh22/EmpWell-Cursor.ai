"""
Test suite for standardized psychological tests.

This module tests the WHO-5 Wellbeing Index and GAD-7 Anxiety Scale
implementations to ensure accurate scoring and interpretation.
"""

import pytest
from typing import List, Dict, Any

from backend.app.core.standardized_tests import (
    WHO5WellbeingIndex,
    GAD7AnxietyScale,
    StandardizedTestRegistry,
    AssessmentResult,
    RiskLevel,
    ScoreInterpretation,
    calculate_who5_score,
    calculate_gad7_score,
    get_test_by_key
)


class TestWHO5WellbeingIndex:
    """Test suite for WHO-5 Wellbeing Index implementation."""
    
    def test_valid_who5_responses(self):
        """Test WHO-5 with valid response sets."""
        # Test case 1: Perfect wellbeing (all 5s)
        perfect_responses = [5, 5, 5, 5, 5]
        result = WHO5WellbeingIndex.calculate_score(perfect_responses)
        
        assert result.raw_score == 25
        assert result.percentage_score == 100.0
        assert result.interpretation == ScoreInterpretation.EXCELLENT
        assert result.risk_level == RiskLevel.VERY_LOW
        assert "excellent" in result.description.lower()
        assert not result.follow_up_suggested
        
        # Test case 2: Poor wellbeing (all 0s)
        poor_responses = [0, 0, 0, 0, 0]
        result = WHO5WellbeingIndex.calculate_score(poor_responses)
        
        assert result.raw_score == 0
        assert result.percentage_score == 0.0
        assert result.interpretation == ScoreInterpretation.POOR
        assert result.risk_level == RiskLevel.VERY_HIGH
        assert "poor" in result.description.lower()
        assert result.follow_up_suggested
        
        # Test case 3: Moderate wellbeing
        moderate_responses = [3, 2, 3, 3, 2]
        result = WHO5WellbeingIndex.calculate_score(moderate_responses)
        
        assert result.raw_score == 13
        assert result.percentage_score == 52.0
        assert result.interpretation == ScoreInterpretation.AVERAGE
        assert result.risk_level == RiskLevel.LOW
    
    def test_who5_edge_cases(self):
        """Test WHO-5 edge cases and boundary values."""
        # Test depression threshold (score = 12 -> 48%)
        boundary_responses = [2, 3, 2, 3, 2]
        result = WHO5WellbeingIndex.calculate_score(boundary_responses)
        
        assert result.raw_score == 12
        assert result.percentage_score == 48.0
        assert result.risk_level == RiskLevel.MODERATE
        
        # Test just above depression threshold (score = 13 -> 52%)
        above_boundary = [3, 2, 3, 2, 3]
        result = WHO5WellbeingIndex.calculate_score(above_boundary)
        
        assert result.raw_score == 13
        assert result.percentage_score == 52.0
        assert result.risk_level == RiskLevel.LOW
    
    def test_who5_invalid_responses(self):
        """Test WHO-5 with invalid response sets."""
        # Too few responses
        with pytest.raises(ValueError, match="exactly 5 responses"):
            WHO5WellbeingIndex.calculate_score([1, 2, 3])
        
        # Too many responses
        with pytest.raises(ValueError, match="exactly 5 responses"):
            WHO5WellbeingIndex.calculate_score([1, 2, 3, 4, 5, 6])
        
        # Invalid response values
        with pytest.raises(ValueError, match="between 0 and 5"):
            WHO5WellbeingIndex.calculate_score([1, 2, 3, 4, 6])
        
        with pytest.raises(ValueError, match="between 0 and 5"):
            WHO5WellbeingIndex.calculate_score([-1, 2, 3, 4, 5])
    
    def test_who5_recommendations(self):
        """Test WHO-5 recommendation generation."""
        # High risk responses
        high_risk = [0, 1, 0, 1, 0]
        result = WHO5WellbeingIndex.calculate_score(high_risk)
        
        assert len(result.recommendations) > 0
        assert any("mental health professional" in rec.lower() for rec in result.recommendations)
        assert result.follow_up_suggested
        
        # Low energy pattern
        low_energy = [3, 3, 0, 3, 3]  # Low score on "active and vigorous"
        result = WHO5WellbeingIndex.calculate_score(low_energy)
        
        assert any("physical activity" in rec.lower() for rec in result.recommendations)
        
        # Sleep issues pattern
        sleep_issues = [3, 3, 3, 0, 3]  # Low score on "fresh and rested"
        result = WHO5WellbeingIndex.calculate_score(sleep_issues)
        
        assert any("sleep" in rec.lower() for rec in result.recommendations)
    
    def test_who5_clinical_considerations(self):
        """Test WHO-5 clinical considerations generation."""
        # Very low score
        very_low = [0, 1, 1, 1, 1]
        result = WHO5WellbeingIndex.calculate_score(very_low)
        
        assert result.clinical_considerations is not None
        assert "depression risk" in result.clinical_considerations.lower()
        
        # Zero responses
        with_zeros = [0, 2, 3, 2, 3]
        result = WHO5WellbeingIndex.calculate_score(with_zeros)
        
        assert result.clinical_considerations is not None
        assert "zero responses" in result.clinical_considerations.lower()
    
    def test_who5_validation(self):
        """Test WHO-5 response validation."""
        # Valid responses
        valid_responses = [1, 2, 3, 4, 5]
        is_valid, errors = WHO5WellbeingIndex.validate_response_set(valid_responses)
        assert is_valid
        assert len(errors) == 0
        
        # Invalid responses
        invalid_responses = [1, 2, 3, 4]  # Too few
        is_valid, errors = WHO5WellbeingIndex.validate_response_set(invalid_responses)
        assert not is_valid
        assert len(errors) > 0


class TestGAD7AnxietyScale:
    """Test suite for GAD-7 Anxiety Scale implementation."""
    
    def test_valid_gad7_responses(self):
        """Test GAD-7 with valid response sets."""
        # No anxiety (all 0s)
        no_anxiety = [0, 0, 0, 0, 0, 0, 0]
        result = GAD7AnxietyScale.calculate_score(no_anxiety)
        
        assert result.raw_score == 0
        assert result.percentage_score == 0.0
        assert result.interpretation == ScoreInterpretation.AVERAGE
        assert result.risk_level == RiskLevel.VERY_LOW
        assert "minimal" in result.description.lower()
        assert not result.follow_up_suggested
        
        # Severe anxiety (all 3s)
        severe_anxiety = [3, 3, 3, 3, 3, 3, 3]
        result = GAD7AnxietyScale.calculate_score(severe_anxiety)
        
        assert result.raw_score == 21
        assert result.percentage_score == 100.0
        assert result.interpretation == ScoreInterpretation.POOR
        assert result.risk_level == RiskLevel.HIGH
        assert "severe" in result.description.lower()
        assert result.follow_up_suggested
        
        # Mild anxiety
        mild_anxiety = [1, 1, 1, 1, 1, 1, 0]
        result = GAD7AnxietyScale.calculate_score(mild_anxiety)
        
        assert result.raw_score == 6
        assert result.interpretation == ScoreInterpretation.BELOW_AVERAGE
        assert result.risk_level == RiskLevel.LOW
    
    def test_gad7_thresholds(self):
        """Test GAD-7 severity thresholds."""
        # Minimal anxiety (0-4)
        minimal = [1, 1, 1, 1, 0, 0, 0]
        result = GAD7AnxietyScale.calculate_score(minimal)
        assert result.risk_level == RiskLevel.VERY_LOW
        
        # Mild anxiety (5-9) 
        mild = [1, 1, 1, 1, 1, 0, 0]
        result = GAD7AnxietyScale.calculate_score(mild)
        assert result.risk_level == RiskLevel.LOW
        
        # Moderate anxiety (10-14)
        moderate = [2, 2, 2, 2, 2, 0, 0]
        result = GAD7AnxietyScale.calculate_score(moderate)
        assert result.risk_level == RiskLevel.MODERATE
        
        # Severe anxiety (15-21)
        severe = [3, 3, 3, 3, 3, 0, 0]
        result = GAD7AnxietyScale.calculate_score(severe)
        assert result.risk_level == RiskLevel.HIGH
    
    def test_gad7_invalid_responses(self):
        """Test GAD-7 with invalid responses."""
        # Wrong number of responses
        with pytest.raises(ValueError, match="exactly 7 responses"):
            GAD7AnxietyScale.calculate_score([1, 2, 3])
        
        # Invalid values
        with pytest.raises(ValueError, match="between 0 and 3"):
            GAD7AnxietyScale.calculate_score([1, 2, 3, 4, 1, 2, 1])
    
    def test_gad7_clinical_considerations(self):
        """Test GAD-7 clinical considerations."""
        # Severe anxiety
        severe = [3, 3, 3, 3, 3, 0, 0]
        result = GAD7AnxietyScale.calculate_score(severe)
        
        assert result.clinical_considerations is not None
        assert "severe anxiety" in result.clinical_considerations.lower()
        
        # High anticipatory anxiety (last question)
        anticipatory = [1, 1, 1, 1, 1, 1, 3]
        result = GAD7AnxietyScale.calculate_score(anticipatory)
        
        assert result.clinical_considerations is not None
        assert "anticipatory anxiety" in result.clinical_considerations.lower()


class TestStandardizedTestRegistry:
    """Test the standardized test registry."""
    
    def test_registry_functionality(self):
        """Test registry operations."""
        # List all tests
        tests = StandardizedTestRegistry.list_tests()
        assert len(tests) >= 2  # At least WHO-5 and GAD-7
        
        test_keys = [test["key"] for test in tests]
        assert "who5" in test_keys
        assert "gad7" in test_keys
        
        # Get specific tests
        who5_class = StandardizedTestRegistry.get_test("who5")
        assert who5_class == WHO5WellbeingIndex
        
        gad7_class = StandardizedTestRegistry.get_test("gad7")
        assert gad7_class == GAD7AnxietyScale
        
        # Non-existent test
        non_existent = StandardizedTestRegistry.get_test("nonexistent")
        assert non_existent is None
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # WHO-5 convenience function
        who5_responses = [3, 3, 3, 3, 3]
        result = calculate_who5_score(who5_responses)
        assert isinstance(result, AssessmentResult)
        assert result.raw_score == 15
        
        # GAD-7 convenience function
        gad7_responses = [1, 1, 1, 1, 1, 1, 1]
        result = calculate_gad7_score(gad7_responses)
        assert isinstance(result, AssessmentResult)
        assert result.raw_score == 7
        
        # Get test by key
        who5_test = get_test_by_key("who5")
        assert who5_test == WHO5WellbeingIndex


class TestStandardizedTestIntegration:
    """Integration tests for standardized tests."""
    
    def test_who5_complete_workflow(self):
        """Test complete WHO-5 workflow."""
        # Get question data
        questions = WHO5WellbeingIndex.get_question_data()
        assert len(questions) == 5
        
        for question in questions:
            assert "text" in question
            assert "options" in question
            assert len(question["options"]) == 6  # WHO-5 has 6 response options
            assert question["type"] == "likert"
            assert question["required"] is True
        
        # Test various response patterns
        test_cases = [
            ([5, 5, 5, 5, 5], "excellent wellbeing"),
            ([0, 0, 0, 0, 0], "depression risk"),
            ([2, 2, 2, 2, 2], "below average"),
            ([4, 4, 4, 4, 4], "good wellbeing")
        ]
        
        for responses, expected_pattern in test_cases:
            result = WHO5WellbeingIndex.calculate_score(responses)
            assert isinstance(result, AssessmentResult)
            assert len(result.recommendations) > 0
            # Check if expected pattern appears in description or recommendations
            text_to_check = (result.description + " " + " ".join(result.recommendations)).lower()
            # This is a loose check since exact wording may vary
            assert any(word in text_to_check for word in expected_pattern.split())
    
    def test_gad7_complete_workflow(self):
        """Test complete GAD-7 workflow."""
        # Test response patterns
        test_cases = [
            ([0, 0, 0, 0, 0, 0, 0], RiskLevel.VERY_LOW),
            ([1, 1, 1, 1, 1, 0, 0], RiskLevel.LOW),
            ([2, 2, 2, 2, 0, 0, 0], RiskLevel.MODERATE),
            ([3, 3, 3, 3, 3, 0, 0], RiskLevel.HIGH)
        ]
        
        for responses, expected_risk in test_cases:
            result = GAD7AnxietyScale.calculate_score(responses)
            assert result.risk_level == expected_risk
            assert len(result.recommendations) > 0
            
            # Check follow-up suggestions for higher risk levels
            if expected_risk in [RiskLevel.MODERATE, RiskLevel.HIGH]:
                assert result.follow_up_suggested
    
    def test_percentile_calculations(self):
        """Test percentile calculations for both tests."""
        # WHO-5 percentiles
        perfect_who5 = WHO5WellbeingIndex.calculate_score([5, 5, 5, 5, 5])
        assert perfect_who5.normative_percentile >= 90
        
        poor_who5 = WHO5WellbeingIndex.calculate_score([0, 0, 0, 0, 0])
        assert poor_who5.normative_percentile <= 10
        
        # GAD-7 percentiles
        no_anxiety = GAD7AnxietyScale.calculate_score([0, 0, 0, 0, 0, 0, 0])
        assert no_anxiety.normative_percentile <= 20
        
        severe_anxiety = GAD7AnxietyScale.calculate_score([3, 3, 3, 3, 3, 3, 3])
        assert severe_anxiety.normative_percentile >= 90
    
    def test_recommendation_quality(self):
        """Test that recommendations are appropriate and helpful."""
        # WHO-5 with sleep issues
        sleep_problem = [3, 3, 3, 0, 3]
        result = WHO5WellbeingIndex.calculate_score(sleep_problem)
        
        sleep_recommendations = [rec for rec in result.recommendations if "sleep" in rec.lower()]
        assert len(sleep_recommendations) > 0
        
        # GAD-7 with high anxiety
        high_anxiety = [3, 3, 3, 3, 2, 2, 2]
        result = GAD7AnxietyScale.calculate_score(high_anxiety)
        
        professional_help = [rec for rec in result.recommendations 
                           if "professional" in rec.lower() or "healthcare" in rec.lower()]
        assert len(professional_help) > 0


# Performance and stress tests
class TestStandardizedTestPerformance:
    """Performance tests for standardized tests."""
    
    def test_calculation_performance(self):
        """Test that calculations are fast enough for real-time use."""
        import time
        
        # Test WHO-5 performance
        start_time = time.time()
        for _ in range(1000):
            WHO5WellbeingIndex.calculate_score([2, 3, 2, 3, 2])
        who5_time = time.time() - start_time
        
        # Should complete 1000 calculations in under 1 second
        assert who5_time < 1.0
        
        # Test GAD-7 performance
        start_time = time.time()
        for _ in range(1000):
            GAD7AnxietyScale.calculate_score([1, 2, 1, 2, 1, 2, 1])
        gad7_time = time.time() - start_time
        
        assert gad7_time < 1.0
    
    def test_memory_efficiency(self):
        """Test that the implementations don't leak memory."""
        import gc
        
        initial_objects = len(gc.get_objects())
        
        # Create many assessment results
        for i in range(100):
            WHO5WellbeingIndex.calculate_score([i % 6, (i+1) % 6, (i+2) % 6, (i+3) % 6, (i+4) % 6])
            GAD7AnxietyScale.calculate_score([i % 4, (i+1) % 4, (i+2) % 4, (i+3) % 4, 
                                            (i+4) % 4, (i+5) % 4, (i+6) % 4])
        
        # Force garbage collection
        gc.collect()
        
        final_objects = len(gc.get_objects())
        
        # Should not have significant memory growth (allow some variance)
        assert final_objects - initial_objects < 1000


# Edge case and error handling tests
class TestStandardizedTestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_boundary_score_interpretations(self):
        """Test interpretations at score boundaries."""
        # WHO-5 boundary cases
        boundary_cases = [
            (12, RiskLevel.MODERATE),  # Just at depression threshold
            (13, RiskLevel.LOW),       # Just above depression threshold
            (50, RiskLevel.MODERATE),  # At 50% boundary
            (51, RiskLevel.LOW),       # Just above 50%
        ]
        
        for percentage_score, expected_risk in boundary_cases:
            # Convert percentage back to raw responses (approximate)
            raw_score = int(percentage_score * 25 / 100)
            # Create dummy responses that sum to raw_score
            responses = [raw_score // 5] * 5
            if raw_score % 5 != 0:
                responses[0] += raw_score % 5
            
            result = WHO5WellbeingIndex.calculate_score(responses)
            assert result.risk_level == expected_risk
    
    def test_extreme_response_patterns(self):
        """Test extreme response patterns."""
        # All minimum responses
        all_min_who5 = [0, 0, 0, 0, 0]
        result = WHO5WellbeingIndex.calculate_score(all_min_who5)
        assert result.risk_level == RiskLevel.VERY_HIGH
        assert result.follow_up_suggested
        
        # All maximum responses
        all_max_who5 = [5, 5, 5, 5, 5]
        result = WHO5WellbeingIndex.calculate_score(all_max_who5)
        assert result.risk_level == RiskLevel.VERY_LOW
        assert not result.follow_up_suggested
        
        # Mixed extreme responses
        mixed_extreme = [0, 5, 0, 5, 0]
        result = WHO5WellbeingIndex.calculate_score(mixed_extreme)
        assert result.clinical_considerations is not None
    
    def test_data_type_handling(self):
        """Test handling of different data types."""
        # Test with integers (normal case)
        int_responses = [1, 2, 3, 4, 5]
        result = WHO5WellbeingIndex.calculate_score(int_responses)
        assert isinstance(result.raw_score, (int, float))
        
        # Test validation with non-integers should work with validation method
        valid, errors = WHO5WellbeingIndex.validate_response_set([1.0, 2.0, 3.0, 4.0, 5.0])
        assert not valid  # Should fail because we expect integers
        assert len(errors) > 0


if __name__ == "__main__":
    # Run some basic tests if script is executed directly
    print("Running basic WHO-5 tests...")
    
    # Test perfect wellbeing
    perfect = WHO5WellbeingIndex.calculate_score([5, 5, 5, 5, 5])
    print(f"Perfect wellbeing: {perfect.percentage_score}% - {perfect.description}")
    
    # Test poor wellbeing
    poor = WHO5WellbeingIndex.calculate_score([0, 0, 0, 0, 0])
    print(f"Poor wellbeing: {poor.percentage_score}% - {poor.description}")
    
    print("\nRunning basic GAD-7 tests...")
    
    # Test no anxiety
    no_anxiety = GAD7AnxietyScale.calculate_score([0, 0, 0, 0, 0, 0, 0])
    print(f"No anxiety: {no_anxiety.raw_score}/21 - {no_anxiety.description}")
    
    # Test severe anxiety
    severe = GAD7AnxietyScale.calculate_score([3, 3, 3, 3, 3, 3, 3])
    print(f"Severe anxiety: {severe.raw_score}/21 - {severe.description}")
    
    print("\nAll basic tests completed successfully!")
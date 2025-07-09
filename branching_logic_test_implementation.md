# Branching Logic Test Implementation

## Overview

This document outlines the comprehensive test scenarios implemented for the dynamic test engine's branching logic functionality. The tests verify conditional question display, proper scoring with branched paths, progress tracking with skipped questions, and validation of branching rules.

## Test Structure

### Test Fixtures

#### 1. `branching_test_template`
A complex test template with 7 questions demonstrating various branching scenarios:

- **Q1**: Entry point question (mood assessment)
- **Q2**: Always shown (exercise frequency)
- **Q3**: Conditional - shown if Q1 ≤ 2 (low mood triggers depression screening)
- **Q4**: Conditional - shown if Q1 ≥ 4 (high mood triggers wellbeing assessment)
- **Q5**: Conditional - shown if Q2 ≥ 3 (regular exercise triggers fitness assessment)
- **Q6**: Nested conditional - shown if Q3 ≥ 3 (high depression score triggers help-seeking)
- **Q7**: Always shown at end (overall satisfaction)

#### 2. Supporting Fixtures
- `test_user`: Creates a test user for assessments
- `test_attempt`: Creates a test attempt for the branching assessment

## Test Cases

### 1. Basic Question Visibility (`test_should_show_question_basic`)
**Purpose**: Verify that questions without conditions are always displayed.
**Coverage**:
- Tests Q1, Q2, Q7 (no branching conditions)
- Validates baseline functionality

### 2. Conditional Display - True Condition (`test_should_show_question_conditional_true`)
**Purpose**: Test conditional question display when condition is met.
**Scenario**:
- Answer Q1 with value 2 (low feeling)
- Verify Q3 is shown (condition: Q1 ≤ 2)
- Verify Q4 is NOT shown (condition: Q1 ≥ 4)

### 3. Conditional Display - False Condition (`test_should_show_question_conditional_false`)
**Purpose**: Test conditional question display when condition is not met.
**Scenario**:
- Answer Q1 with value 5 (high feeling)
- Verify Q3 is NOT shown (condition: Q1 ≤ 2)
- Verify Q4 is shown (condition: Q1 ≥ 4)

### 4. Nested Conditional Questions (`test_nested_conditional_questions`)
**Purpose**: Test nested branching logic (Q6 depends on Q3, which depends on Q1).
**Scenario**:
- Answer Q1 with value 1 (very low feeling) → triggers Q3
- Answer Q3 with value 4 (high sadness) → triggers Q6
- Verify both conditions are properly evaluated

### 5. Linear Path Navigation (`test_get_next_question_linear_path`)
**Purpose**: Test question progression without branching triggers.
**Flow**:
- Start with Q1
- Answer Q1 with high value (5) → skips Q3
- Next question should be Q2

### 6. Branching Path Navigation (`test_get_next_question_branching_path`)
**Purpose**: Test question progression with branching triggers.
**Flow**:
- Answer Q1 with low value (1) → should trigger Q3 after Q2
- Answer Q2 → next question should be Q3

### 7. Score Calculation with Skipped Questions (`test_calculate_score_with_skipped_questions`)
**Purpose**: Verify scoring accuracy when questions are skipped due to branching.
**Verification**:
- Only answered questions contribute to score
- Proper weight application
- Normalized score within 0-100 range

### 8. Progress Tracking (`test_progress_tracking_with_skipped_questions`)
**Purpose**: Test progress calculation accounting for skipped questions.
**Metrics**:
- Answered count accuracy
- Total questions estimation
- Percentage calculation

### 9. Branching Rules Validation - Valid Rules (`test_validate_branching_rules_valid`)
**Purpose**: Ensure the test template has valid branching configuration.
**Verification**:
- No validation errors
- Rules are logically consistent

### 10. Circular Dependency Detection (`test_validate_branching_rules_circular_dependency`)
**Purpose**: Test detection of circular dependencies in branching rules.
**Scenario**:
- Create Q1 depending on Q2
- Create Q2 depending on Q1
- Verify circular dependency is detected

### 11. Invalid Reference Detection (`test_validate_branching_rules_invalid_reference`)
**Purpose**: Test detection of invalid question references.
**Scenario**:
- Create question referencing non-existent question ID
- Verify invalid reference is detected

### 12. Complex Branching Scenario (`test_complex_branching_scenario`)
**Purpose**: Test comprehensive branching with multiple conditions.
**Scenario**: Low mood + high exercise path
- Q1 = 2 (low mood) → triggers Q3
- Q2 = 5 (high exercise) → triggers Q5
- Q3 = 3 (high sadness) → triggers Q6
- Verify Q4 is skipped (Q1 not ≥ 4)
- Calculate final score with all branches

### 13. API Integration Test (`test_branching_with_client_api`)
**Purpose**: Test branching logic through actual API endpoints.
**Flow**:
- Login authentication
- Start test attempt
- Navigate through questions with branching
- Verify API responses and final results

## Helper Functions

### `should_show_question()`
**Purpose**: Core branching logic evaluation
**Logic**:
- Returns True for questions without conditions
- Evaluates conditional logic based on previous responses
- Supports ≤ and ≥ comparisons

### `get_next_question()`
**Purpose**: Determine next question in branching sequence
**Process**:
1. Get all template questions ordered by sequence
2. Get existing responses
3. Find first unanswered question that should be shown
4. Return None if test complete

### `calculate_test_score()`
**Purpose**: Score calculation with branching considerations
**Method**:
- Normalize response values to 0-1 scale
- Apply question weights
- Calculate raw and percentage scores
- Account for skipped questions

### `get_test_progress()`
**Purpose**: Progress tracking with branching estimation
**Calculation**:
- Count answered questions
- Estimate remaining questions based on current path
- Provide percentage completion

### `validate_branching_rules()`
**Purpose**: Comprehensive branching rule validation
**Checks**:
- Circular dependency detection using DFS
- Invalid question reference validation
- Logical consistency of condition values

## Branching Logic Design

### Condition Evaluation
The branching logic uses a simple threshold-based system:
- **Low threshold values (≤ 3)**: Use ≤ comparison
- **High threshold values (> 3)**: Use ≥ comparison

### Question Flow
1. Questions are ordered by sequence number
2. Conditional questions evaluated against previous responses
3. Skipped questions don't affect scoring or progress
4. Test completion when no more questions should be shown

### Error Handling
- Invalid references detected during validation
- Circular dependencies prevented
- Graceful handling of missing responses

## Testing Strategy

### Coverage Areas
✅ **Conditional Display**: Questions shown/hidden based on conditions
✅ **Nested Conditions**: Multi-level branching dependencies  
✅ **Score Calculation**: Accurate scoring with skipped questions
✅ **Progress Tracking**: Dynamic progress estimation
✅ **Rule Validation**: Comprehensive validation of branching rules
✅ **API Integration**: End-to-end testing through REST endpoints
✅ **Edge Cases**: Circular dependencies, invalid references

### Test Data Quality
- Realistic assessment scenarios (mood, exercise, wellbeing)
- Comprehensive branching patterns
- Edge case coverage
- API authentication integration

## Implementation Benefits

1. **Reliability**: Comprehensive test coverage ensures robust branching logic
2. **Maintainability**: Clear test structure makes future modifications safer
3. **Documentation**: Tests serve as living documentation of branching behavior
4. **Quality Assurance**: Validation functions prevent configuration errors
5. **User Experience**: Proper progress tracking and scoring with dynamic content

## Future Enhancements

1. **Complex Conditions**: Support for AND/OR logic combinations
2. **Value Ranges**: Branching based on value ranges rather than single thresholds
3. **Question Types**: Support for different question types (multiple choice, text)
4. **Dynamic Scoring**: Adaptive scoring algorithms based on branching paths
5. **Performance Optimization**: Caching strategies for large branching trees
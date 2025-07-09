# Branching Logic Implementation

## Overview

This document describes the implementation of the core branching logic functionality for the dynamic test engine. The system provides sophisticated conditional question display, adaptive scoring, and intelligent progress tracking for personalized assessments.

## Architecture

### Core Components

#### 1. QuestionDisplayController
**Purpose**: Controls which questions should be displayed based on branching conditions.

**Key Methods**:
- `should_show_question()`: Evaluates if a question should be shown
- `get_visible_questions()`: Returns all questions visible for current state
- `get_next_question()`: Determines the next question in sequence

**Logic**:
- Smart threshold evaluation (≤ 3 uses ≤ comparison, > 3 uses ≥ comparison)
- Backward compatibility with existing model structure
- Real-time evaluation based on previous responses

#### 2. BranchingRulesProcessor
**Purpose**: Validates and processes branching rules for test templates.

**Key Methods**:
- `validate_branching_rules()`: Comprehensive rule validation
- `get_branching_tree()`: Visual representation of branching structure
- Circular dependency detection using DFS algorithm
- Invalid reference detection
- Logical inconsistency checks

#### 3. BranchingScoreCalculator
**Purpose**: Handles score calculation for tests with branching logic.

**Features**:
- Weighted scoring with normalization
- Dimensional score calculation for personality tests
- Proper handling of skipped questions
- Raw and normalized score calculation

#### 4. BranchingProgressTracker
**Purpose**: Tracks progress through tests with dynamic question sets.

**Capabilities**:
- Dynamic progress estimation
- Question path tracking
- Completion detection
- Adaptive total question estimation

## API Endpoints

### Test Management
- `POST /{key}/start` - Start a new test attempt
- `GET /{key}/question` - Get next question with branching logic
- `POST /{key}/answer` - Submit answer and trigger branching
- `GET /{key}/results` - Get final results with dimensional scores
- `GET /{key}/progress` - Get current progress with estimation

### Validation & Analysis
- `GET /{key}/validate` - Validate branching rules
- `GET /{key}/branching-tree` - Get visual branching structure

## Branching Logic Features

### 1. Conditional Question Display
```python
# Example: Show depression screening if mood is low
question.show_if_question_id = mood_question.id
question.show_if_value = 2  # Show if mood ≤ 2
```

### 2. Nested Conditions
Support for multi-level dependencies:
- Q6 depends on Q3, which depends on Q1
- Proper evaluation order and dependency resolution

### 3. Smart Threshold Logic
```python
# Intelligent comparison logic
if threshold <= 3:
    return response_value <= threshold  # Low values use ≤
else:
    return response_value >= threshold  # High values use ≥
```

### 4. Advanced Operators (Extensible)
```python
class BranchingOperator(str, Enum):
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN_RANGE = "in_range"
    NOT_IN_RANGE = "not_in_range"
```

## Scoring System

### Weighted Scoring
- Each question has configurable weight
- Normalization to 0-1 scale before applying weights
- Percentage-based final scores

### Dimensional Scoring
Support for multi-dimensional assessments:
```python
dimensional_scores = {
    "EI": {  # Extraversion-Introversion
        "raw_score": 2.4,
        "normalized_score": 48.0,
        "positive_letter": "E"
    }
}
```

### Skipped Question Handling
- Only answered questions contribute to score
- Proper weight adjustment for missing questions
- Maintains scoring accuracy with dynamic content

## Progress Tracking

### Dynamic Estimation
```python
{
    "percentage": 66.7,
    "answered_count": 4,
    "total_questions": 6,
    "visible_questions": 5,
    "potential_additional": 2,
    "is_complete": False
}
```

### Question Path Tracking
Records the actual path taken through the assessment:
```python
path = [
    {
        "question_id": 1,
        "order": 1,
        "text": "How are you feeling today?",
        "response_value": 2,
        "was_conditional": False,
        "condition_met": True
    }
]
```

## Validation System

### Circular Dependency Detection
Uses depth-first search to detect circular references:
```python
def has_circular_dependency(question_id, visited, recursion_stack):
    if question_id in recursion_stack:
        return True  # Circular dependency found
```

### Validation Types
1. **Circular Dependencies**: Prevents infinite loops
2. **Invalid References**: Ensures referenced questions exist
3. **Logical Inconsistencies**: Validates condition values against question ranges

## Sample Data

### Wellbeing Assessment
8-question adaptive assessment with branching based on:
- Mood level (triggers depression screening)
- Exercise frequency (triggers fitness questions)
- Life satisfaction (triggers work-life balance questions)

### Personality Assessment
6-question adaptive personality test with branching on:
- Social preference (extraversion vs. introversion paths)
- Conscientiousness level (detail-oriented follow-ups)

### Stress Assessment
5-question targeted stress assessment focusing on:
- Overall stress level (determines specific stressor exploration)
- High stress triggers (sleep impact assessment)

## Integration Points

### Database Models
Leverages existing `Question` model fields:
- `show_if_question_id`: Reference to conditional question
- `show_if_value`: Threshold value for condition
- `weight`: Question weight for scoring
- `dimension_pair`: For dimensional scoring

### Legacy Compatibility
- Maintains backward compatibility with existing tests
- Graceful fallback for non-branching assessments
- Enhanced scoring for all test types

## Error Handling

### Validation Errors
```python
{
    "template_key": "test_key",
    "is_valid": False,
    "errors": [
        "Circular dependency detected involving question 3",
        "Question 5 references non-existent question 99"
    ]
}
```

### Runtime Safety
- Graceful handling of missing responses
- Proper validation of answer ranges
- Prevention of duplicate responses

## Performance Considerations

### Optimization Strategies
1. **Efficient Queries**: Minimal database hits using proper joins
2. **Caching**: Question visibility evaluation caching
3. **Lazy Loading**: Progressive question evaluation
4. **Batch Operations**: Efficient response processing

### Scalability
- Supports complex branching trees (tested up to 50+ questions)
- Efficient validation algorithms
- Minimal memory footprint for progress tracking

## Usage Examples

### Starting a Branching Assessment
```python
# Start test
response = client.post("/tests/wellbeing_branching/start")
attempt_id = response.json()["attempt_id"]

# Get first question
response = client.get("/tests/wellbeing_branching/question")
question = response.json()

# Submit answer
client.post("/tests/wellbeing_branching/answer", {
    "question_id": question["id"],
    "value": 2  # Low mood - will trigger depression screening
})
```

### Validation Check
```python
# Validate branching rules
response = client.get("/tests/wellbeing_branching/validate")
validation = response.json()

if not validation["is_valid"]:
    print("Validation errors:", validation["errors"])
```

## Future Enhancements

### Advanced Features
1. **Complex Conditions**: AND/OR logic combinations
2. **Value Ranges**: Multi-threshold conditions
3. **Question Types**: Support for different input types
4. **Machine Learning**: Adaptive branching based on user patterns
5. **Real-time Analytics**: Live branching pattern analysis

### Performance Improvements
1. **Caching Layers**: Redis-based question visibility cache
2. **Async Processing**: Non-blocking score calculation
3. **Database Optimization**: Query optimization for large datasets
4. **CDN Integration**: Static content delivery for question assets

## Testing Strategy

### Comprehensive Test Coverage
- Unit tests for all branching logic components
- Integration tests for API endpoints
- End-to-end tests for complete user journeys
- Performance tests for large branching trees

### Test Scenarios
- Linear paths (no branching)
- Complex branching scenarios
- Edge cases (circular dependencies, invalid references)
- Error conditions and recovery

## Deployment Notes

### Configuration
- Environment-specific branching rules
- Feature flags for gradual rollout
- Monitoring and alerting setup

### Migration Strategy
- Backward-compatible implementation
- Gradual migration of existing tests
- Data validation and integrity checks

The branching logic implementation provides a robust, scalable foundation for adaptive assessments while maintaining compatibility with existing systems and ensuring reliable, accurate results for all users.
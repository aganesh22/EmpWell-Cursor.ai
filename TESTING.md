# Testing Guide

This document outlines the testing strategy and practices for the Corporate Wellbeing Platform.

## Test Structure

```
backend/tests/
├── conftest.py           # Pytest configuration and fixtures
├── test_basic.py         # Basic functionality tests
├── test_auth.py          # Authentication tests
├── test_comprehensive.py # Full feature tests
└── test_security.py      # Security-focused tests
```

## Running Tests

### Local Development
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
cd backend && python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_auth.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Docker Environment
```bash
# Run tests in Docker
docker compose run --rm backend pytest tests/ -v

# Run with database
docker compose up -d db
docker compose run --rm backend pytest tests/ -v
```

### CI/CD Pipeline
Tests run automatically on:
- Every push to main/master branches
- All pull requests
- Scheduled nightly runs (recommended)

## Test Categories

### 1. Unit Tests (`test_basic.py`)
- Basic functionality verification
- Import validation
- Simple component tests
- **Coverage**: Core utilities, models, schemas

### 2. Integration Tests (`test_auth.py`, `test_comprehensive.py`)
- API endpoint testing
- Database interactions
- Authentication flows
- **Coverage**: Full request/response cycles

### 3. Security Tests (`test_security.py`)
- Authentication security
- Input validation
- SQL injection prevention
- Authorization checks
- **Coverage**: Security vulnerabilities

## Test Fixtures

### Database Fixture
```python
@pytest.fixture
def test_session(test_engine):
    """Isolated database session for each test."""
    with Session(test_engine) as session:
        yield session
```

### Client Fixture
```python
@pytest.fixture
def client(test_session):
    """FastAPI test client with database override."""
    # Dependency injection for testing
```

## Test Data Management

### In-Memory Database
- Tests use SQLite in-memory database
- No external dependencies required
- Automatic cleanup between tests

### Test Data Isolation
- Each test gets fresh database session
- No test data persistence between runs
- Predictable test environment

## Security Testing

### Authentication Tests
- JWT token validation
- Password hashing verification
- Role-based access control
- Session management

### Input Validation Tests
- SQL injection prevention
- XSS protection
- Email format validation
- Data sanitization

### Privacy Tests
- User enumeration prevention
- Information disclosure checks
- Error message security

## Performance Testing

### Basic Performance
```bash
# Load testing with pytest-benchmark
pip install pytest-benchmark
python -m pytest tests/ --benchmark-only
```

### Database Performance
- Query optimization verification
- Connection pooling tests
- Index effectiveness

## Code Coverage

### Coverage Requirements
- **Minimum**: 80% overall coverage
- **Target**: 90% for critical paths
- **Critical**: 100% for security functions

### Coverage Reports
```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Exclusions
- Test files themselves
- Migration scripts
- Development-only code

## Mocking and Test Doubles

### External Service Mocking
```python
# Email service mocking
@patch('backend.app.notifications._send_email')
def test_notification_sending(mock_send):
    mock_send.return_value = True
    # Test logic here
```

### Database Mocking
- Use test database instead of mocking
- Real SQLModel operations
- Actual constraint validation

## Test Environment Setup

### Environment Variables
```bash
# Test-specific environment
DATABASE_URL=sqlite:///:memory:
SECRET_KEY=test-secret-key
GOOGLE_CLIENT_ID=fake-google-client-id
```

### Test Configuration
```python
# conftest.py settings
TEST_DATABASE_URL = "sqlite:///:memory:"
TESTING = True
```

## Continuous Integration

### GitHub Actions Workflow
1. **Setup**: Python 3.11, PostgreSQL service
2. **Dependencies**: Install requirements
3. **Database**: Wait for PostgreSQL ready
4. **Tests**: Run pytest with verbose output
5. **Security**: Bandit and Safety scans
6. **Reports**: Upload coverage reports

### Test Failure Handling
- **Flaky Tests**: Retry mechanism for network-dependent tests
- **Debugging**: Verbose output for CI failures
- **Notifications**: Slack/email on test failures

## Best Practices

### Writing Tests
1. **Descriptive Names**: Test function names explain what they test
2. **Single Responsibility**: One test per behavior
3. **Arrange-Act-Assert**: Clear test structure
4. **Independent Tests**: No dependencies between tests

### Test Data
1. **Minimal Data**: Only create necessary test data
2. **Realistic Data**: Use production-like data formats
3. **Edge Cases**: Test boundary conditions
4. **Error Cases**: Test failure scenarios

### Performance
1. **Fast Tests**: Keep test execution time minimal
2. **Parallel Execution**: Use pytest-xdist for parallel runs
3. **Resource Cleanup**: Proper teardown to prevent leaks

## Debugging Failed Tests

### Local Debugging
```bash
# Run single test with debugging
python -m pytest tests/test_auth.py::test_login_success -v -s --pdb

# Capture output
python -m pytest tests/ -v -s --capture=no
```

### CI Debugging
- Check GitHub Actions logs
- Review test output and stack traces
- Verify environment variable setup
- Check database connectivity

### Common Issues
1. **Import Errors**: Check Python path and module structure
2. **Database Errors**: Verify connection string and permissions
3. **Authentication Errors**: Check JWT secret and token format
4. **Timeout Errors**: Increase timeout for slow operations

## Test Metrics

### Success Criteria
- ✅ All tests pass consistently
- ✅ Coverage above 80%
- ✅ Security tests pass
- ✅ Performance within limits

### Monitoring
- Test execution time trends
- Coverage percentage tracking
- Failure rate monitoring
- Security scan results

For questions about testing, contact the development team or refer to the pytest documentation.
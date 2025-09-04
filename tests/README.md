# Party Drink Tracker - Test Suite

This directory contains comprehensive unit tests for the Party Drink Tracker application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── README.md                   # This file
├── test_models/                # Model tests
│   ├── __init__.py
│   └── test_guest.py          # Guest model and BAC calculation tests
│   └── test_drink.py          # Drink and DrinkConsumption model tests
├── test_routes/               # Route tests
│   ├── __init__.py
│   ├── test_guest_routes.py   # Guest interface route tests
│   └── test_host_routes.py    # Host interface route tests
├── test_bac_calculation/      # BAC calculation specific tests
│   ├── __init__.py
│   └── test_bac_logic.py      # Scientific accuracy tests
├── test_constants/            # Constants validation tests
│   ├── __init__.py
│   └── test_constants.py      # Constants validation and integration
└── test_app/                  # Flask application tests
    ├── __init__.py
    └── test_app.py           # App configuration and integration tests
```

## Running Tests

### Quick Test Run
```bash
python run_tests.py
```

### Manual Test Run
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m models          # Model tests only
pytest -m routes          # Route tests only
pytest -m bac            # BAC calculation tests only

# Run specific test files
pytest tests/test_models/test_guest.py
pytest tests/test_bac_calculation/
```

## Test Categories

### Model Tests (`test_models/`)
- Guest creation and validation
- Drink creation and alcohol calculations
- DrinkConsumption relationships
- BAC calculation accuracy
- Database relationships

### Route Tests (`test_routes/`)
- Guest interface routes
- Host interface routes
- API endpoints
- Template rendering
- Error handling

### BAC Calculation Tests (`test_bac_calculation/`)
- Scientific accuracy of Widmark formula
- Metabolism calculations over time
- Edge cases and boundary conditions
- Real-world drinking scenarios

### Constants Tests (`test_constants/`)
- Validation of scientific constants
- Unit conversion accuracy
- Integration between constants

### App Tests (`test_app/`)
- Flask application configuration
- Blueprint registration
- Database integration
- Error handling

## Test Fixtures

The `conftest.py` file provides shared fixtures for testing:

- `app`: Flask application instance
- `client`: Test client for making requests
- `db_session`: Database session for tests
- `sample_guest`: Pre-created guest for testing
- `sample_drink`: Pre-created drink for testing
- `sample_consumption`: Pre-created consumption for testing
- `multiple_consumptions`: Multiple consumptions for BAC testing

## Coverage Requirements

Tests are configured to require 80% code coverage. Coverage reports are generated in:
- Terminal output (`--cov-report=term-missing`)
- HTML format (`htmlcov/index.html`)

## Writing New Tests

### Adding Test Categories
1. Create new subdirectory under `tests/`
2. Add `__init__.py` file
3. Create test files following naming convention `test_*.py`

### Test Naming Conventions
- Test functions: `test_*`
- Test classes: `Test*`
- Test modules: `test_*`

### Using Fixtures
```python
def test_my_feature(client, db_session, sample_guest):
    # Test code here
    pass
```

## Continuous Integration

The test suite is designed to work with CI/CD pipelines and includes:
- Proper exit codes for automation
- Coverage reporting for quality metrics
- Marker-based test selection
- Comprehensive error reporting

## Dependencies

Test dependencies are included in `requirements.txt`:
- pytest: Test framework
- pytest-cov: Coverage reporting
- pytest-flask: Flask-specific testing utilities
- pytest-mock: Mocking utilities

Copyright (C) 2025 Brighter Sight

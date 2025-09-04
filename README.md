# 🍻 Party Drink Tracker

A web-accessible application to track party drinks and monitor estimated blood alcohol content (BAC) levels.

## Features

- **Guest Interface** (port 4000)
  - Select your name from the guest list
  - Enter your weight for accurate BAC calculation
  - Choose drinks from a visual grid of options
  - Track your drink consumption throughout the party

- **Host Interface** (port 4001)
  - Dashboard showing all guests' drink consumption
  - Real-time BAC estimation graphs
  - Individual and group BAC visualization
  - Monitor guests' drinking patterns

## Setup Instructions

### Prerequisites

- Python 3.7+
- Virtual environment

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/party-drink-tracker.git
   cd party-drink-tracker
   ```

2. Set up and activate the virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize sample data (optional):
   ```
   python init_sample_data.py
   ```

### Data Files

The application uses the following data files:

- `~/guest-list`: A text file with one guest name per line
- `~/drinks/drink-list.csv`: CSV file with drink metadata (name, ABV, volume, image)
- `~/drinks/`: Directory containing drink images

Sample files will be created when you run `init_sample_data.py`.

## Running the Application

1. Start the guest interface (port 4000):
   ```
   python run.py
   ```

2. Start the host interface (port 4001) in a separate terminal:
   ```
   python run_host.py
   ```

3. Access the interfaces:
   - Guest interface: `http://<ip-address>:4000`
   - Host interface: `http://<ip-address>:4001`

## Testing

The application includes a comprehensive unit test suite to ensure code quality and functionality.

### Running Tests

#### Quick Test Run
```bash
python run_tests.py
```

#### Manual Test Execution
```bash
# Install test dependencies (included in requirements.txt)
pip install -r requirements.txt

# Run all tests with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m models        # Test data models
pytest -m routes        # Test API routes
pytest -m bac          # Test BAC calculations
pytest -m unit         # Run unit tests only

# Run specific test files
pytest tests/test_models/test_guest.py
pytest tests/test_bac_calculation/
```

### Test Structure

The test suite is organized into the following directories:

- **`tests/test_models/`** - Model layer tests (Guest, Drink, DrinkConsumption)
- **`tests/test_routes/`** - Route/API endpoint tests
- **`tests/test_bac_calculation/`** - BAC calculation scientific accuracy tests
- **`tests/test_constants/`** - Constants validation tests
- **`tests/test_app/`** - Flask application configuration tests

### Test Coverage

- ✅ **80% minimum code coverage** required
- ✅ **HTML coverage reports** generated in `htmlcov/`
- ✅ **Terminal coverage output** with `--cov-report=term-missing`
- ✅ **CI/CD ready** with proper exit codes

### Test Documentation

See `tests/README.md` for detailed information about:
- Test organization and structure
- Writing new tests
- Test fixtures and utilities
- Coverage requirements
- Development workflow

## Usage

### For Guests

1. Select your name from the guest list
2. Enter your weight (for accurate BAC calculation)
3. Click on a drink whenever you consume one
4. Your drink history will be displayed and tracked

### For Hosts

1. View the dashboard showing all guests' consumption
2. Monitor the group BAC chart to see everyone's levels
3. Click "View Chart" for any guest to see their individual BAC timeline
4. Data refreshes automatically every minute

## License

This program is free software under GPL v3

Copyright (C) 2025 Brighter Sight

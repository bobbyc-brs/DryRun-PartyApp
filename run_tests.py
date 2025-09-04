#!/usr/bin/env python3
"""
Test runner script for Party Drink Tracker.

This script runs all unit tests with coverage reporting.

Copyright (C) 2025 Brighter Sight
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For inquiries, contact: Info@BrighterSight.ca
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage."""
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Install test dependencies if needed
    print("Installing test dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "-r", "requirements.txt"
    ], check=True)

    # Run tests with coverage
    print("\nRunning tests with coverage...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "--verbose",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=80"
    ])

    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("Coverage report saved to htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(result.returncode)

if __name__ == "__main__":
    run_tests()

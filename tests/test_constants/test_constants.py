"""
Unit tests for application constants and their validation.

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

import pytest
from app.constants import *


class TestBACConstants:
    """Test BAC-related constants."""

    def test_ethanol_density(self):
        """Test ethanol density constant."""
        # Ethanol density should be around 0.789 g/ml
        assert 0.780 <= ETHANOL_DENSITY_G_PER_ML <= 0.800

    def test_gender_constants(self):
        """Test gender distribution constants."""
        # Female constant should be lower than male (less body water)
        assert FEMALE_GENDER_CONSTANT < MALE_GENDER_CONSTANT

        # Average should be between male and female
        assert FEMALE_GENDER_CONSTANT <= AVERAGE_GENDER_CONSTANT <= MALE_GENDER_CONSTANT

        # All should be in physiologically reasonable range
        assert 0.50 <= FEMALE_GENDER_CONSTANT <= 0.60
        assert 0.65 <= MALE_GENDER_CONSTANT <= 0.75
        assert 0.55 <= AVERAGE_GENDER_CONSTANT <= 0.70

    def test_metabolism_rate(self):
        """Test BAC metabolism rate."""
        # Should be around 0.015% per hour
        assert 0.010 <= BAC_METABOLISM_RATE <= 0.020

    def test_legal_limit(self):
        """Test legal BAC limit."""
        # Most jurisdictions use 0.08%
        assert BAC_LEGAL_LIMIT == 0.08

    def test_display_cap(self):
        """Test BAC display cap."""
        # Should be higher than legal limit
        assert BAC_DISPLAY_CAP > BAC_LEGAL_LIMIT
        # Should be reasonable (not too high)
        assert BAC_DISPLAY_CAP <= 1.0

    def test_decimal_precision(self):
        """Test BAC decimal precision."""
        # Should be reasonable precision
        assert 2 <= BAC_DECIMAL_PRECISION <= 4


class TestUnitConversionConstants:
    """Test unit conversion constants."""

    def test_pounds_to_kilograms(self):
        """Test pounds to kilograms conversion."""
        # 1 lb should equal approximately 0.453592 kg
        assert 0.4535 <= LBS_TO_KG_CONVERSION <= 0.4537

        # Test conversion accuracy
        assert abs(150 * LBS_TO_KG_CONVERSION - 68.0388) < 0.001
        assert abs(200 * LBS_TO_KG_CONVERSION - 90.7184) < 0.001


class TestTimeConstants:
    """Test time-related constants."""

    def test_bac_history_hours(self):
        """Test BAC history duration."""
        # Should be reasonable history length
        assert 1 <= BAC_HISTORY_HOURS <= 24

    def test_bac_interval_minutes(self):
        """Test BAC calculation interval."""
        # Should be reasonable interval
        assert 5 <= BAC_INTERVAL_MINUTES <= 60
        # Should divide evenly into hours
        assert 60 % BAC_INTERVAL_MINUTES == 0


class TestUIConstants:
    """Test UI-related constants."""

    def test_chart_heights(self):
        """Test chart height constants."""
        # Should be reasonable pixel values
        assert 300 <= CHART_HEIGHT_INDIVIDUAL <= 800
        assert 400 <= CHART_HEIGHT_GROUP <= 1000

        # Group chart should be taller than individual
        assert CHART_HEIGHT_GROUP > CHART_HEIGHT_INDIVIDUAL

    def test_marker_size(self):
        """Test drink marker size."""
        # Should be reasonable pixel size
        assert 5 <= DRINK_MARKER_SIZE <= 20


class TestServerConstants:
    """Test server-related constants."""

    def test_port_numbers(self):
        """Test server port numbers."""
        # Should be valid port numbers
        assert 1024 <= GUEST_PORT <= 65535
        assert 1024 <= HOST_PORT <= 65535

        # Should be different ports
        assert GUEST_PORT != HOST_PORT

    def test_file_paths(self):
        """Test file path constants."""
        # Should be reasonable paths
        assert DEFAULT_GUEST_LIST_PATH.endswith("guest-list")
        assert DEFAULT_DRINK_LIST_PATH.endswith("drink-list.csv")
        assert DEFAULT_DRINKS_DIR.endswith("drinks")


class TestConstantsIntegration:
    """Test constants work together properly."""

    def test_bac_calculation_constants(self):
        """Test that BAC calculation constants work together."""
        # Test a sample BAC calculation
        weight_lbs = 150
        alcohol_grams = 14.0  # One beer
        gender_constant = AVERAGE_GENDER_CONSTANT

        # Manual calculation
        weight_grams = weight_lbs * LBS_TO_KG_CONVERSION * 1000
        bac = (alcohol_grams / (weight_grams * gender_constant)) * 100

        # Should be reasonable
        assert 0.02 <= bac <= 0.05

        # After metabolism
        metabolized_bac = BAC_METABOLISM_RATE * 2  # 2 hours
        bac_after_metabolism = max(0, bac - metabolized_bac)

        # Should be lower
        assert bac_after_metabolism < bac
        assert bac_after_metabolism >= 0

    def test_time_interval_calculations(self):
        """Test time interval calculations."""
        total_intervals = (BAC_HISTORY_HOURS * 60) // BAC_INTERVAL_MINUTES

        # Should be reasonable number of intervals
        assert 10 <= total_intervals <= 200

        # Should be able to calculate timestamps
        intervals = list(range(0, BAC_HISTORY_HOURS * 60 + 1, BAC_INTERVAL_MINUTES))
        assert len(intervals) == total_intervals + 1


class TestConstantsTypeValidation:
    """Test that constants have correct types."""

    def test_numeric_constants(self):
        """Test that numeric constants are actually numbers."""
        numeric_constants = [
            ETHANOL_DENSITY_G_PER_ML,
            AVERAGE_GENDER_CONSTANT,
            MALE_GENDER_CONSTANT,
            FEMALE_GENDER_CONSTANT,
            LBS_TO_KG_CONVERSION,
            BAC_METABOLISM_RATE,
            BAC_LEGAL_LIMIT,
            BAC_DISPLAY_CAP,
            BAC_HISTORY_HOURS,
            BAC_INTERVAL_MINUTES,
            CHART_HEIGHT_INDIVIDUAL,
            CHART_HEIGHT_GROUP,
            DRINK_MARKER_SIZE,
            GUEST_PORT,
            HOST_PORT,
            BAC_DECIMAL_PRECISION
        ]

        for const in numeric_constants:
            assert isinstance(const, (int, float))

    def test_string_constants(self):
        """Test that string constants are actually strings."""
        string_constants = [
            DEFAULT_GUEST_LIST_PATH,
            DEFAULT_DRINK_LIST_PATH,
            DEFAULT_DRINKS_DIR
        ]

        for const in string_constants:
            assert isinstance(const, str)

    def test_positive_values(self):
        """Test that constants that should be positive are positive."""
        positive_constants = [
            ETHANOL_DENSITY_G_PER_ML,
            AVERAGE_GENDER_CONSTANT,
            MALE_GENDER_CONSTANT,
            FEMALE_GENDER_CONSTANT,
            LBS_TO_KG_CONVERSION,
            BAC_METABOLISM_RATE,
            BAC_LEGAL_LIMIT,
            BAC_DISPLAY_CAP,
            BAC_HISTORY_HOURS,
            BAC_INTERVAL_MINUTES,
            CHART_HEIGHT_INDIVIDUAL,
            CHART_HEIGHT_GROUP,
            DRINK_MARKER_SIZE,
            GUEST_PORT,
            HOST_PORT,
            BAC_DECIMAL_PRECISION
        ]

        for const in positive_constants:
            assert const > 0

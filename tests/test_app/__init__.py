"""
Flask app unit tests for Party Drink Tracker.

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
from datetime import datetime, timezone, timedelta
from app import get_local_time, format_local_time


class TestTimezoneUtilities:
    """Test timezone conversion utilities."""

    def test_get_local_time_with_naive_datetime(self):
        """Test get_local_time with naive datetime (should assume UTC)."""
        # Create a naive datetime (no timezone info)
        utc_naive = datetime(2025, 1, 15, 12, 30, 45)

        # Convert to local time
        local_time = get_local_time(utc_naive)

        # Should have timezone info now
        assert local_time.tzinfo is not None

        # The time should be adjusted for local timezone
        # We can't predict the exact offset, but it should be a valid datetime
        assert isinstance(local_time, datetime)

    def test_get_local_time_with_utc_datetime(self):
        """Test get_local_time with UTC datetime."""
        # Create a UTC datetime
        utc_dt = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)

        # Convert to local time
        local_time = get_local_time(utc_dt)

        # Should have timezone info
        assert local_time.tzinfo is not None
        assert isinstance(local_time, datetime)

    def test_format_local_time_basic(self):
        """Test format_local_time with basic formatting."""
        # Create a UTC datetime
        utc_dt = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)

        # Format as local time
        formatted = format_local_time(utc_dt, '%H:%M:%S')

        # Should return a string
        assert isinstance(formatted, str)
        # Should be in HH:MM:SS format
        assert len(formatted) == 8  # HH:MM:SS is 8 characters
        assert ':' in formatted

    def test_format_local_time_with_date(self):
        """Test format_local_time with date formatting."""
        # Create a UTC datetime
        utc_dt = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)

        # Format as local time with date
        formatted = format_local_time(utc_dt, '%Y-%m-%d %H:%M')

        # Should return a string
        assert isinstance(formatted, str)
        # Should contain expected date format
        assert '2025' in formatted
        assert ':' in formatted

    def test_format_local_time_different_formats(self):
        """Test format_local_time with different strftime formats."""
        utc_dt = datetime(2025, 1, 15, 14, 25, 30, tzinfo=timezone.utc)

        # Test 24-hour format
        time_24h = format_local_time(utc_dt, '%H:%M')
        assert isinstance(time_24h, str)

        # Test 12-hour format
        time_12h = format_local_time(utc_dt, '%I:%M %p')
        assert isinstance(time_12h, str)
        assert any(ampm in time_12h.upper() for ampm in ['AM', 'PM'])

    def test_timezone_consistency(self):
        """Test that multiple calls to timezone functions are consistent."""
        utc_dt = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)

        # Get local time multiple times
        local1 = get_local_time(utc_dt)
        local2 = get_local_time(utc_dt)

        # Should be the same (timezone conversion is deterministic)
        assert local1 == local2

        # Format multiple times
        format1 = format_local_time(utc_dt, '%H:%M:%S')
        format2 = format_local_time(utc_dt, '%H:%M:%S')

        # Should be the same
        assert format1 == format2

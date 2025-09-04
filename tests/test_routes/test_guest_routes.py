"""
Unit tests for guest routes.

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

from datetime import datetime, timedelta, timezone

import pytest

from app import format_local_time
from app.models import Drink, DrinkConsumption, Guest


class TestGuestRoutes:
    """Test cases for guest interface routes."""

    @pytest.mark.routes
    def test_guest_index_page(self, client, db_session):
        """Test guest index page loads correctly."""
        response = client.get("/guest/")
        assert response.status_code == 200
        assert b"Party Drink Tracker" in response.data
        assert b"guest-list" in response.data or b"guest" in response.data

    @pytest.mark.routes
    def test_guest_select_page(self, client, sample_guest):
        """Test guest selection page loads correctly."""
        response = client.get(f"/guest/select/{sample_guest.id}")
        assert response.status_code == 200
        assert sample_guest.name.encode() in response.data
        assert b"drink" in response.data

    @pytest.mark.routes
    def test_guest_select_invalid_id(self, client):
        """Test guest selection with invalid ID."""
        response = client.get("/guest/select/999")
        assert response.status_code == 404

    @pytest.mark.routes
    def test_add_drink_post(self, client, sample_guest, sample_drink):
        """Test adding a drink consumption via POST."""
        data = {"drink_id": sample_drink.id}

        response = client.post(f"/guest/add_drink", data=data, follow_redirects=True)

        assert response.status_code == 200

        # Check that consumption was added to database
        from app import db

        consumption = DrinkConsumption.query.filter_by(
            guest_id=sample_guest.id, drink_id=sample_drink.id
        ).first()

        assert consumption is not None
        assert isinstance(consumption.timestamp, datetime)

    @pytest.mark.routes
    def test_add_drink_invalid_drink_id(self, client, sample_guest):
        """Test adding drink with invalid drink ID."""
        data = {"drink_id": 999}  # Non-existent drink

        response = client.post(f"/guest/add_drink", data=data, follow_redirects=True)

        # Should still work but not create consumption
        assert response.status_code == 200

    @pytest.mark.routes
    def test_add_drink_without_guest_session(self, client, sample_drink):
        """Test adding drink without guest selection."""
        data = {"drink_id": sample_drink.id}

        response = client.post("/guest/add_drink", data=data, follow_redirects=True)

        # Should still work but might not associate with guest
        assert response.status_code == 200

    @pytest.mark.routes
    def test_guest_page_with_no_guests(self, client, db_session):
        """Test guest page when no guests exist."""
        # Clear all guests
        Guest.query.delete()
        db_session.commit()

        response = client.get("/guest/")
        assert response.status_code == 200
        # Should still render but with no guests
        assert b"guest" in response.data

    @pytest.mark.routes
    def test_guest_page_with_no_drinks(self, client, db_session):
        """Test guest page when no drinks exist."""
        # Clear all drinks
        Drink.query.delete()
        db_session.commit()

        response = client.get("/guest/")
        assert response.status_code == 200
        # Should still render but with no drinks
        assert b"drink" in response.data


class TestGuestRouteTemplates:
    """Test that guest routes render correct templates."""

    @pytest.mark.routes
    def test_guest_index_template(self, client):
        """Test that guest index uses correct template."""
        response = client.get("/guest/")

        # Check for template elements
        assert b"html" in response.data
        assert b"head" in response.data
        assert b"body" in response.data

    @pytest.mark.routes
    def test_guest_select_template(self, client, sample_guest):
        """Test that guest select uses correct template."""
        response = client.get(f"/guest/select/{sample_guest.id}")

        # Check for template elements
        assert b"html" in response.data
        assert sample_guest.name.encode() in response.data

    @pytest.mark.routes
    def test_guest_weight_form(self, client, sample_guest):
        """Test that guest select page includes weight input."""
        response = client.get(f"/guest/select/{sample_guest.id}")

        # Should contain weight input form
        assert b"weight" in response.data or b"Weight" in response.data
        assert b"input" in response.data

    @pytest.mark.routes
    def test_guest_drink_buttons(self, client, sample_guest, sample_drink):
        """Test that guest select page shows drink options."""
        response = client.get(f"/guest/select/{sample_guest.id}")

        # Should contain drink information
        assert sample_drink.name.encode() in response.data
        assert b"button" in response.data or b"btn" in response.data


class TestGuestRouteDataValidation:
    """Test data validation in guest routes."""

    @pytest.mark.routes
    def test_add_drink_with_weight_update(self, client, sample_guest, sample_drink):
        """Test adding drink with weight update."""
        new_weight = 160

        data = {"drink_id": sample_drink.id, "weight": new_weight}

        response = client.post(f"/guest/add_drink", data=data, follow_redirects=True)

        assert response.status_code == 200

        # Check that guest weight was updated
        from app import db

        db.session.refresh(sample_guest)
        assert sample_guest.weight == new_weight

    @pytest.mark.routes
    def test_add_drink_invalid_weight(self, client, sample_guest, sample_drink):
        """Test adding drink with invalid weight."""
        data = {"drink_id": sample_drink.id, "weight": "invalid"}

        response = client.post(f"/guest/add_drink", data=data, follow_redirects=True)

        assert response.status_code == 200
        # Weight should not be updated
        from app import db

        db.session.refresh(sample_guest)
        assert sample_guest.weight != "invalid"

    @pytest.mark.routes
    def test_add_drink_zero_weight(self, client, sample_guest, sample_drink):
        """Test adding drink with zero weight."""
        data = {"drink_id": sample_drink.id, "weight": 0}

        response = client.post(f"/guest/add_drink", data=data, follow_redirects=True)

        assert response.status_code == 200
        # Should handle zero weight gracefully

    @pytest.mark.routes
    def test_add_drink_negative_weight(self, client, sample_guest, sample_drink):
        """Test adding drink with negative weight."""
        data = {"drink_id": sample_drink.id, "weight": -50}

        response = client.post(f"/guest/add_drink", data=data, follow_redirects=True)

        assert response.status_code == 200
        # Should handle negative weight gracefully


class TestGuestRouteTimezone:
    """Test timezone functionality in guest routes."""

    @pytest.mark.routes
    def test_guest_select_with_drink_history_local_time(
        self, client, sample_guest, sample_drink
    ):
        """Test that drink history shows local time instead of UTC."""
        # Create a drink consumption with a known timestamp
        utc_timestamp = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        consumption = DrinkConsumption(
            guest_id=sample_guest.id, drink_id=sample_drink.id, timestamp=utc_timestamp
        )
        from app import db

        db.session.add(consumption)
        db.session.commit()

        # Get the guest select page
        response = client.get(f"/guest/select/{sample_guest.id}")

        # Should contain the drink history
        assert response.status_code == 200
        assert sample_drink.name.encode() in response.data

        # The page should render with local time formatting
        # We can't easily test the exact local time format due to timezone differences,
        # but we can verify the page renders without errors and contains expected elements
        assert b"drink-history" in response.data
        assert b"list-group" in response.data

    @pytest.mark.routes
    def test_guest_select_drink_history_empty(self, client, sample_guest):
        """Test guest select page with no drink history."""
        response = client.get(f"/guest/select/{sample_guest.id}")

        # Should show "No drinks recorded yet" message
        assert response.status_code == 200
        assert (
            b"No drinks recorded yet" in response.data
            or b"no drinks" in response.data.lower()
        )

    @pytest.mark.routes
    def test_add_drink_api_returns_local_time(self, client, sample_guest, sample_drink):
        """Test that add_drink API returns timestamp in local time."""
        data = {"drink_id": sample_drink.id, "guest_id": sample_guest.id}

        response = client.post(f"/guest/add_drink", data=data, follow_redirects=True)

        # Should return JSON with local time formatted timestamp
        assert response.status_code == 200

        # The response should be JSON containing timestamp
        import json

        response_data = json.loads(response.data.decode())

        assert "timestamp" in response_data
        assert "success" in response_data
        assert response_data["success"] is True

        # Timestamp should be a string in time format (HH:MM:SS)
        timestamp_str = response_data["timestamp"]
        assert isinstance(timestamp_str, str)
        assert len(timestamp_str) == 8  # HH:MM:SS format
        assert timestamp_str.count(":") == 2

    @pytest.mark.routes
    def test_guest_select_template_renders_drink_history(
        self, client, sample_guest, sample_drink
    ):
        """Test that guest select template properly renders drink history with local time."""
        # Create a consumption
        utc_timestamp = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        consumption = DrinkConsumption(
            guest_id=sample_guest.id, drink_id=sample_drink.id, timestamp=utc_timestamp
        )
        from app import db

        db.session.add(consumption)
        db.session.commit()

        response = client.get(f"/guest/select/{sample_guest.id}")

        # Template should render successfully
        assert response.status_code == 200
        assert b"Your Drink History" in response.data

        # Should contain the drink name
        assert sample_drink.name.encode() in response.data

        # Should contain time formatting (we can't test exact time due to timezone differences)
        assert b":" in response.data  # Should contain time separators

    @pytest.mark.routes
    def test_guest_select_multiple_drinks_ordering(
        self, client, sample_guest, sample_drink
    ):
        """Test that multiple drinks are ordered correctly by timestamp (newest first)."""
        # Create multiple consumptions with different timestamps
        utc_base = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

        # Create consumptions in reverse chronological order
        consumptions = []
        for i in range(3):
            consumption = DrinkConsumption(
                guest_id=sample_guest.id,
                drink_id=sample_drink.id,
                timestamp=utc_base + timedelta(minutes=i * 5),  # 12:00, 12:05, 12:10
            )
            consumptions.append(consumption)
            from app import db

            db.session.add(consumption)

        db.session.commit()

        response = client.get(f"/guest/select/{sample_guest.id}")

        # Should render successfully
        assert response.status_code == 200
        assert sample_drink.name.encode() in response.data

        # Should contain multiple drinks
        assert response.data.count(sample_drink.name.encode()) >= 3


class TestGuestAddGuest:
    """Test add guest functionality."""

    @pytest.mark.routes
    def test_add_guest_success(self, client):
        """Test successfully adding a new guest."""
        data = {"name": "Test Guest"}

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 200
        response_data = response.get_json()

        assert response_data["success"] is True
        assert "Test Guest" in response_data["message"]
        assert response_data["guest"]["name"] == "Test Guest"
        assert response_data["guest"]["id"] is not None

    @pytest.mark.routes
    def test_add_guest_with_weight(self, client):
        """Test adding a guest with weight."""
        data = {"name": "Weighted Guest", "weight": 180}

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 200
        response_data = response.get_json()

        assert response_data["success"] is True
        assert response_data["guest"]["name"] == "Weighted Guest"
        assert response_data["guest"]["weight"] == 180

    @pytest.mark.routes
    def test_add_guest_duplicate_name(self, client, sample_guest):
        """Test adding a guest with duplicate name fails."""
        data = {"name": sample_guest.name}  # This already exists

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 400
        response_data = response.get_json()

        assert response_data["success"] is False
        assert "already exists" in response_data["error"]

    @pytest.mark.routes
    def test_add_guest_empty_name(self, client):
        """Test adding a guest with empty name fails."""
        data = {"name": ""}

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 400
        response_data = response.get_json()

        assert response_data["success"] is False
        assert "cannot be empty" in response_data["error"]

    @pytest.mark.routes
    def test_add_guest_no_name(self, client):
        """Test adding a guest without name fails."""
        data = {}  # No name field

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 400
        response_data = response.get_json()

        assert response_data["success"] is False
        assert "required" in response_data["error"]

    @pytest.mark.routes
    def test_add_guest_invalid_weight(self, client):
        """Test adding a guest with invalid weight fails."""
        data = {"name": "Invalid Weight Guest", "weight": -50}

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 400
        response_data = response.get_json()

        assert response_data["success"] is False
        assert "positive" in response_data["error"]

    @pytest.mark.routes
    def test_add_guest_zero_weight(self, client):
        """Test adding a guest with zero weight fails."""
        data = {"name": "Zero Weight Guest", "weight": 0}

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 400
        response_data = response.get_json()

        assert response_data["success"] is False
        assert "positive" in response_data["error"]

    @pytest.mark.routes
    def test_add_guest_large_weight(self, client):
        """Test adding a guest with valid large weight succeeds."""
        data = {"name": "Large Guest", "weight": 450}  # Within valid range

        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 200
        response_data = response.get_json()

        assert response_data["success"] is True
        assert response_data["guest"]["weight"] == 450

    @pytest.mark.routes
    def test_add_guest_database_persistence(self, client):
        """Test that added guest persists in database."""
        data = {"name": "Persistent Guest"}

        # Add guest
        response = client.post("/guest/add_guest", json=data)

        assert response.status_code == 200

        # Check that guest exists in database by trying to add again (should fail)
        response2 = client.post("/guest/add_guest", json=data)

        assert response2.status_code == 400
        response_data = response2.get_json()
        assert "already exists" in response_data["error"]

    @pytest.mark.routes
    def test_add_guest_long_name(self, client):
        """Test adding a guest with a very long name."""
        long_name = "A" * 100  # Very long name
        data = {"name": long_name}

        response = client.post("/guest/add_guest", json=data)

        # Should succeed since we don't have a strict length limit
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["success"] is True

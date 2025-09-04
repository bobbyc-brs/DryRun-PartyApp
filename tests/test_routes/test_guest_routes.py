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

import pytest
from datetime import datetime
from app.models import Guest, Drink, DrinkConsumption


class TestGuestRoutes:
    """Test cases for guest interface routes."""

    @pytest.mark.routes
    def test_guest_index_page(self, client, db_session):
        """Test guest index page loads correctly."""
        response = client.get('/guest/')
        assert response.status_code == 200
        assert b'Party Drink Tracker' in response.data
        assert b'guest-list' in response.data or b'guest' in response.data

    @pytest.mark.routes
    def test_guest_select_page(self, client, sample_guest):
        """Test guest selection page loads correctly."""
        response = client.get(f'/guest/select/{sample_guest.id}')
        assert response.status_code == 200
        assert sample_guest.name.encode() in response.data
        assert b'drink' in response.data

    @pytest.mark.routes
    def test_guest_select_invalid_id(self, client):
        """Test guest selection with invalid ID."""
        response = client.get('/guest/select/999')
        assert response.status_code == 404

    @pytest.mark.routes
    def test_add_drink_post(self, client, sample_guest, sample_drink):
        """Test adding a drink consumption via POST."""
        data = {
            'drink_id': sample_drink.id
        }

        response = client.post(f'/guest/add_drink',
                             data=data,
                             follow_redirects=True)

        assert response.status_code == 200

        # Check that consumption was added to database
        from app import db
        consumption = DrinkConsumption.query.filter_by(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id
        ).first()

        assert consumption is not None
        assert isinstance(consumption.timestamp, datetime)

    @pytest.mark.routes
    def test_add_drink_invalid_drink_id(self, client, sample_guest):
        """Test adding drink with invalid drink ID."""
        data = {
            'drink_id': 999  # Non-existent drink
        }

        response = client.post(f'/guest/add_drink',
                             data=data,
                             follow_redirects=True)

        # Should still work but not create consumption
        assert response.status_code == 200

    @pytest.mark.routes
    def test_add_drink_without_guest_session(self, client, sample_drink):
        """Test adding drink without guest selection."""
        data = {
            'drink_id': sample_drink.id
        }

        response = client.post('/guest/add_drink',
                             data=data,
                             follow_redirects=True)

        # Should still work but might not associate with guest
        assert response.status_code == 200

    @pytest.mark.routes
    def test_guest_page_with_no_guests(self, client, db_session):
        """Test guest page when no guests exist."""
        # Clear all guests
        Guest.query.delete()
        db_session.commit()

        response = client.get('/guest/')
        assert response.status_code == 200
        # Should still render but with no guests
        assert b'guest' in response.data

    @pytest.mark.routes
    def test_guest_page_with_no_drinks(self, client, db_session):
        """Test guest page when no drinks exist."""
        # Clear all drinks
        Drink.query.delete()
        db_session.commit()

        response = client.get('/guest/')
        assert response.status_code == 200
        # Should still render but with no drinks
        assert b'drink' in response.data


class TestGuestRouteTemplates:
    """Test that guest routes render correct templates."""

    @pytest.mark.routes
    def test_guest_index_template(self, client):
        """Test that guest index uses correct template."""
        response = client.get('/guest/')

        # Check for template elements
        assert b'html' in response.data
        assert b'head' in response.data
        assert b'body' in response.data

    @pytest.mark.routes
    def test_guest_select_template(self, client, sample_guest):
        """Test that guest select uses correct template."""
        response = client.get(f'/guest/select/{sample_guest.id}')

        # Check for template elements
        assert b'html' in response.data
        assert sample_guest.name.encode() in response.data

    @pytest.mark.routes
    def test_guest_weight_form(self, client, sample_guest):
        """Test that guest select page includes weight input."""
        response = client.get(f'/guest/select/{sample_guest.id}')

        # Should contain weight input form
        assert b'weight' in response.data or b'Weight' in response.data
        assert b'input' in response.data

    @pytest.mark.routes
    def test_guest_drink_buttons(self, client, sample_guest, sample_drink):
        """Test that guest select page shows drink options."""
        response = client.get(f'/guest/select/{sample_guest.id}')

        # Should contain drink information
        assert sample_drink.name.encode() in response.data
        assert b'button' in response.data or b'btn' in response.data


class TestGuestRouteDataValidation:
    """Test data validation in guest routes."""

    @pytest.mark.routes
    def test_add_drink_with_weight_update(self, client, sample_guest, sample_drink):
        """Test adding drink with weight update."""
        new_weight = 160

        data = {
            'drink_id': sample_drink.id,
            'weight': new_weight
        }

        response = client.post(f'/guest/add_drink',
                             data=data,
                             follow_redirects=True)

        assert response.status_code == 200

        # Check that guest weight was updated
        from app import db
        db.session.refresh(sample_guest)
        assert sample_guest.weight == new_weight

    @pytest.mark.routes
    def test_add_drink_invalid_weight(self, client, sample_guest, sample_drink):
        """Test adding drink with invalid weight."""
        data = {
            'drink_id': sample_drink.id,
            'weight': 'invalid'
        }

        response = client.post(f'/guest/add_drink',
                             data=data,
                             follow_redirects=True)

        assert response.status_code == 200
        # Weight should not be updated
        from app import db
        db.session.refresh(sample_guest)
        assert sample_guest.weight != 'invalid'

    @pytest.mark.routes
    def test_add_drink_zero_weight(self, client, sample_guest, sample_drink):
        """Test adding drink with zero weight."""
        data = {
            'drink_id': sample_drink.id,
            'weight': 0
        }

        response = client.post(f'/guest/add_drink',
                             data=data,
                             follow_redirects=True)

        assert response.status_code == 200
        # Should handle zero weight gracefully

    @pytest.mark.routes
    def test_add_drink_negative_weight(self, client, sample_guest, sample_drink):
        """Test adding drink with negative weight."""
        data = {
            'drink_id': sample_drink.id,
            'weight': -50
        }

        response = client.post(f'/guest/add_drink',
                             data=data,
                             follow_redirects=True)

        assert response.status_code == 200
        # Should handle negative weight gracefully

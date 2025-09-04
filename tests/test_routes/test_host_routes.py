"""
Unit tests for host routes.

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
import json
from datetime import datetime, timedelta
from app.models import Guest, Drink, DrinkConsumption


class TestHostDashboardRoutes:
    """Test cases for host dashboard routes."""

    @pytest.mark.routes
    def test_host_dashboard_page(self, client):
        """Test host dashboard page loads correctly."""
        response = client.get('/host/')
        assert response.status_code == 200
        assert b'Host Dashboard' in response.data or b'dashboard' in response.data

    @pytest.mark.routes
    def test_guest_data_endpoint(self, client, db_session):
        """Test guest data API endpoint."""
        response = client.get('/host/guest_data')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

        # Should contain guest information
        if data:  # If there are guests
            guest_data = data[0]
            assert 'id' in guest_data
            assert 'name' in guest_data
            assert 'weight' in guest_data
            assert 'bac' in guest_data
            assert 'drinks' in guest_data

    @pytest.mark.routes
    def test_bac_chart_endpoint(self, client, sample_guest):
        """Test individual BAC chart endpoint."""
        response = client.get(f'/host/bac_chart/{sample_guest.id}')
        assert response.status_code == 200

        # Should return JSON data
        data = json.loads(response.data)
        assert 'data' in data
        assert 'layout' in data

        # Should have BAC line data
        assert len(data['data']) >= 1

    @pytest.mark.routes
    def test_bac_chart_invalid_guest(self, client):
        """Test BAC chart with invalid guest ID."""
        response = client.get('/host/bac_chart/999')
        assert response.status_code == 404

    @pytest.mark.routes
    def test_group_bac_chart_endpoint(self, client):
        """Test group BAC chart endpoint."""
        response = client.get('/host/group_bac_chart')
        assert response.status_code == 200

        # Should return JSON data
        data = json.loads(response.data)
        assert 'data' in data
        assert 'layout' in data

    @pytest.mark.routes
    def test_guest_without_weight_bac_chart(self, client, db_session):
        """Test BAC chart for guest without weight."""
        guest = Guest(name="No Weight Guest", weight=None)
        db_session.add(guest)
        db_session.commit()

        response = client.get(f'/host/bac_chart/{guest.id}')
        # Should handle gracefully
        assert response.status_code in [200, 400]  # 400 if error handling implemented


class TestHostRouteData:
    """Test data returned by host routes."""

    @pytest.mark.routes
    def test_guest_data_structure(self, client, sample_guest, sample_drink, db_session):
        """Test structure of guest data returned by API."""
        # Add a consumption
        consumption = DrinkConsumption(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        response = client.get('/host/guest_data')
        data = json.loads(response.data)

        assert len(data) >= 1
        guest_data = next((g for g in data if g['id'] == sample_guest.id), None)
        assert guest_data is not None

        # Check data structure
        assert guest_data['name'] == sample_guest.name
        assert guest_data['weight'] == sample_guest.weight
        assert isinstance(guest_data['bac'], (float, int))
        assert isinstance(guest_data['drinks'], list)

        # Check drink data structure
        if guest_data['drinks']:
            drink_info = guest_data['drinks'][0]
            assert 'id' in drink_info
            assert 'name' in drink_info
            assert 'timestamp' in drink_info

    @pytest.mark.routes
    def test_bac_chart_data_structure(self, client, sample_guest, sample_drink, db_session):
        """Test structure of BAC chart data."""
        # Add consumption
        consumption = DrinkConsumption(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        response = client.get(f'/host/bac_chart/{sample_guest.id}')
        data = json.loads(response.data)

        # Check basic structure
        assert 'data' in data
        assert 'layout' in data
        assert len(data['data']) >= 1

        # Check first trace (BAC line)
        bac_trace = data['data'][0]
        assert 'x' in bac_trace
        assert 'y' in bac_trace
        assert 'type' in bac_trace
        assert bac_trace['type'] == 'scatter'

        # Check layout
        assert 'title' in data['layout']
        assert 'xaxis' in data['layout']
        assert 'yaxis' in data['layout']

    @pytest.mark.routes
    def test_group_chart_multiple_guests(self, client, db_session):
        """Test group chart with multiple guests."""
        # Create multiple guests with drinks
        guest1 = Guest(name="Guest A", weight=150)
        guest2 = Guest(name="Guest B", weight=160)
        beer = Drink.query.filter_by(name="Beer").first()

        db_session.add_all([guest1, guest2])

        # Add drinks for both guests
        consumption1 = DrinkConsumption(
            guest_id=guest1.id,
            drink_id=beer.id,
            timestamp=datetime.utcnow()
        )
        consumption2 = DrinkConsumption(
            guest_id=guest2.id,
            drink_id=beer.id,
            timestamp=datetime.utcnow()
        )

        db_session.add_all([consumption1, consumption2])
        db_session.commit()

        response = client.get('/host/group_bac_chart')
        data = json.loads(response.data)

        # Should have multiple traces (one per guest)
        assert len(data['data']) >= 2

        # Check that guest names appear in data
        guest_names = [trace.get('name', '') for trace in data['data']]
        assert any('Guest A' in name or 'A' in name for name in guest_names)
        assert any('Guest B' in name or 'B' in name for name in guest_names)


class TestHostRouteEdgeCases:
    """Test edge cases for host routes."""

    @pytest.mark.routes
    def test_guest_data_empty_database(self, client, db_session):
        """Test guest data endpoint with empty database."""
        # Clear all data
        Guest.query.delete()
        Drink.query.delete()
        DrinkConsumption.query.delete()
        db_session.commit()

        response = client.get('/host/guest_data')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data == []

    @pytest.mark.routes
    def test_bac_chart_no_consumptions(self, client, db_session):
        """Test BAC chart for guest with no drink consumptions."""
        guest = Guest(name="No Drinks", weight=150)
        db_session.add(guest)
        db_session.commit()

        response = client.get(f'/host/bac_chart/{guest.id}')
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should still return valid chart data
        assert 'data' in data
        assert 'layout' in data

    @pytest.mark.routes
    def test_group_chart_no_guests(self, client, db_session):
        """Test group chart with no guests."""
        # Clear guests but keep drinks
        Guest.query.delete()
        db_session.commit()

        response = client.get('/host/group_bac_chart')
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return valid chart data (possibly empty or with message)
        assert 'data' in data
        assert 'layout' in data

    @pytest.mark.routes
    def test_bac_chart_very_old_consumption(self, client, sample_guest, sample_drink, db_session):
        """Test BAC chart with very old consumption."""
        # Add consumption from 24 hours ago
        old_time = datetime.utcnow() - timedelta(hours=24)
        consumption = DrinkConsumption(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id,
            timestamp=old_time
        )
        db_session.add(consumption)
        db_session.commit()

        response = client.get(f'/host/bac_chart/{sample_guest.id}')
        assert response.status_code == 200

        data = json.loads(response.data)
        # BAC should be very low or zero due to metabolism
        bac_values = data['data'][0]['y']
        # Most recent values should be very low
        recent_bac = bac_values[-1] if bac_values else 0
        assert recent_bac >= 0
        assert recent_bac < 0.01  # Should be very low after 24 hours


class TestHostRouteTemplates:
    """Test that host routes render correct templates."""

    @pytest.mark.routes
    def test_host_dashboard_template(self, client):
        """Test that host dashboard uses correct template."""
        response = client.get('/host/')

        # Check for template elements
        assert b'html' in response.data
        assert b'head' in response.data
        assert b'body' in response.data

        # Should contain chart containers
        assert b'chart' in response.data or b'div' in response.data

    @pytest.mark.routes
    def test_host_dashboard_guest_list(self, client, sample_guest):
        """Test that host dashboard shows guest list."""
        response = client.get('/host/')

        # Should contain guest information
        assert sample_guest.name.encode() in response.data

    @pytest.mark.routes
    def test_host_dashboard_empty(self, client, db_session):
        """Test host dashboard with no guests."""
        Guest.query.delete()
        db_session.commit()

        response = client.get('/host/')
        assert response.status_code == 200
        # Should still render properly

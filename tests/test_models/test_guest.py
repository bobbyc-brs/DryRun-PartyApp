"""
Unit tests for Guest model and BAC calculations.

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
from datetime import datetime, timedelta
from app.models import Guest, Drink, DrinkConsumption
from app.constants import BAC_DISPLAY_CAP


class TestGuestModel:
    """Test cases for the Guest model."""

    @pytest.mark.models
    def test_guest_creation(self, db_session):
        """Test creating a new guest."""
        guest = Guest(name="Test Guest", weight=160)
        db_session.add(guest)
        db_session.commit()

        assert guest.id is not None
        assert guest.name == "Test Guest"
        assert guest.weight == 160
        assert isinstance(guest.drinks, list)

    @pytest.mark.models
    def test_guest_str_representation(self, sample_guest):
        """Test the string representation of a guest."""
        expected = f"Guest('{sample_guest.name}')"
        assert str(sample_guest) == expected

    @pytest.mark.models
    def test_guest_without_weight(self, db_session):
        """Test BAC calculation for guest without weight."""
        guest = Guest(name="No Weight", weight=None)
        db_session.add(guest)
        db_session.commit()

        assert guest.calculate_bac() == 0.0

    @pytest.mark.models
    def test_guest_zero_weight(self, db_session):
        """Test BAC calculation for guest with zero weight."""
        guest = Guest(name="Zero Weight", weight=0)
        db_session.add(guest)
        db_session.commit()

        assert guest.calculate_bac() == 0.0

    @pytest.mark.models
    def test_guest_no_drinks(self, db_session):
        """Test BAC calculation for guest with no drinks."""
        guest = Guest(name="No Drinks", weight=150)
        db_session.add(guest)
        db_session.commit()

        assert guest.calculate_bac() == 0.0


class TestBACCalculation:
    """Test cases for BAC calculation logic."""

    @pytest.mark.bac
    def test_single_beer_bac(self, sample_guest, sample_drink, db_session):
        """Test BAC calculation for a single beer."""
        # Add a beer consumption
        consumption = DrinkConsumption(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        bac = sample_guest.calculate_bac()

        # Beer: 5% ABV, 355ml = ~14g alcohol
        # Weight: 150lbs = ~68039g
        # Expected BAC: (14 / (68039 * 0.62)) * 100 = ~0.033%
        assert 0.02 <= bac <= 0.05  # Reasonable range for a beer
        assert bac < BAC_DISPLAY_CAP

    @pytest.mark.bac
    def test_multiple_drinks_bac(self, sample_guest, db_session):
        """Test BAC calculation with multiple drinks."""
        beer = Drink.query.filter_by(name="Beer").first()
        wine = Drink.query.filter_by(name="Wine").first()

        # Add multiple consumptions
        base_time = datetime.utcnow()
        consumptions = [
            DrinkConsumption(guest_id=sample_guest.id, drink_id=beer.id,
                           timestamp=base_time - timedelta(hours=1)),
            DrinkConsumption(guest_id=sample_guest.id, drink_id=wine.id,
                           timestamp=base_time - timedelta(minutes=30)),
            DrinkConsumption(guest_id=sample_guest.id, drink_id=beer.id,
                           timestamp=base_time - timedelta(minutes=10))
        ]

        for consumption in consumptions:
            db_session.add(consumption)
        db_session.commit()

        bac = sample_guest.calculate_bac()

        # Should be higher than single beer but still reasonable
        assert bac > 0.05
        assert bac < 0.3  # Should not be unrealistically high
        assert bac < BAC_DISPLAY_CAP

    @pytest.mark.bac
    def test_bac_metabolism_over_time(self, sample_guest, sample_drink, db_session):
        """Test that BAC decreases over time due to metabolism."""
        # Add a drink 2 hours ago
        consumption = DrinkConsumption(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id,
            timestamp=datetime.utcnow() - timedelta(hours=2)
        )
        db_session.add(consumption)
        db_session.commit()

        bac = sample_guest.calculate_bac()

        # After 2 hours, BAC should be significantly reduced
        # Metabolism rate is 0.015% per hour
        # Expected reduction: 2 * 0.015 = 0.03%
        # So BAC should be original - 0.03, but not negative
        assert bac >= 0.0
        assert bac < 0.05  # Should be much lower after 2 hours

    @pytest.mark.bac
    def test_bac_display_cap(self, db_session):
        """Test that BAC is capped at display limit."""
        # Create a guest with very high alcohol consumption
        guest = Guest(name="Heavy Drinker", weight=100)  # Light weight
        db_session.add(guest)

        # Create a high-ABV drink
        strong_drink = Drink(name="High ABV Drink", abv=50.0, volume_ml=500,
                           image_path="images/drinks/strong.png")
        db_session.add(strong_drink)
        db_session.commit()

        # Add multiple strong drinks
        for _ in range(5):
            consumption = DrinkConsumption(
                guest_id=guest.id,
                drink_id=strong_drink.id,
                timestamp=datetime.utcnow()
            )
            db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # BAC should be capped at display limit
        assert bac <= BAC_DISPLAY_CAP

    @pytest.mark.bac
    def test_bac_calculation_precision(self, sample_guest, sample_drink, db_session):
        """Test that BAC calculation returns proper decimal precision."""
        consumption = DrinkConsumption(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        bac = sample_guest.calculate_bac()

        # Should be rounded to 3 decimal places as per constants
        bac_str = f"{bac:.10f}"
        decimal_part = bac_str.split('.')[1]
        # Should not have more than 3 decimal places of precision
        assert len(decimal_part.rstrip('0')) <= 3


class TestGuestRelationships:
    """Test cases for Guest model relationships."""

    @pytest.mark.models
    def test_guest_drink_relationship(self, sample_guest, sample_drink, db_session):
        """Test the relationship between Guest and DrinkConsumption."""
        consumption = DrinkConsumption(
            guest_id=sample_guest.id,
            drink_id=sample_drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        # Refresh the guest from database
        db_session.refresh(sample_guest)

        assert len(sample_guest.drinks) == 1
        assert sample_guest.drinks[0].drink.name == "Beer"
        assert sample_guest.drinks[0].drink.abv == 5.0

    @pytest.mark.models
    def test_guest_multiple_consumptions(self, sample_guest, db_session):
        """Test guest with multiple drink consumptions."""
        beer = Drink.query.filter_by(name="Beer").first()
        wine = Drink.query.filter_by(name="Wine").first()

        # Add multiple consumptions
        consumptions = [
            DrinkConsumption(guest_id=sample_guest.id, drink_id=beer.id,
                           timestamp=datetime.utcnow() - timedelta(hours=2)),
            DrinkConsumption(guest_id=sample_guest.id, drink_id=wine.id,
                           timestamp=datetime.utcnow() - timedelta(hours=1)),
            DrinkConsumption(guest_id=sample_guest.id, drink_id=beer.id,
                           timestamp=datetime.utcnow() - timedelta(minutes=30))
        ]

        for consumption in consumptions:
            db_session.add(consumption)
        db_session.commit()

        # Refresh the guest from database
        db_session.refresh(sample_guest)

        assert len(sample_guest.drinks) == 3

        # Test BAC calculation with multiple drinks
        bac = sample_guest.calculate_bac()
        assert bac > 0
        assert bac < BAC_DISPLAY_CAP

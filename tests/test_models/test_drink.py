"""
Unit tests for Drink and DrinkConsumption models.

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

from datetime import datetime, timedelta

import pytest

from app.models import Drink, DrinkConsumption, Guest


class TestDrinkModel:
    """Test cases for the Drink model."""

    @pytest.mark.models
    def test_drink_creation(self, db_session):
        """Test creating a new drink."""
        drink = Drink(
            name="Test Beer",
            abv=4.5,
            volume_ml=330,
            image_path="images/drinks/test_beer.png",
        )
        db_session.add(drink)
        db_session.commit()

        assert drink.id is not None
        assert drink.name == "Test Beer"
        assert drink.abv == 4.5
        assert drink.volume_ml == 330
        assert drink.image_path == "images/drinks/test_beer.png"

    @pytest.mark.models
    def test_drink_str_representation(self, sample_drink):
        """Test the string representation of a drink."""
        expected = f"Drink('{sample_drink.name}', ABV: {sample_drink.abv}%, Volume: {sample_drink.volume_ml}ml)"
        assert str(sample_drink) == expected

    @pytest.mark.models
    def test_drink_alcohol_calculation(self, db_session):
        """Test alcohol content calculation for different drinks."""
        test_drinks = [
            {
                "name": "Light Beer",
                "abv": 4.0,
                "volume_ml": 355,
                "expected_alcohol": 12.74,
            },
            {"name": "Wine", "abv": 12.0, "volume_ml": 150, "expected_alcohol": 14.22},
            {
                "name": "Whiskey",
                "abv": 40.0,
                "volume_ml": 45,
                "expected_alcohol": 14.31,
            },
        ]

        for drink_data in test_drinks:
            drink = Drink(
                name=drink_data["name"],
                abv=drink_data["abv"],
                volume_ml=drink_data["volume_ml"],
                image_path="images/drinks/test.png",
            )
            db_session.add(drink)
            db_session.commit()

            # Calculate alcohol content manually
            alcohol_grams = (drink.abv * drink.volume_ml * 0.789) / 100

            assert abs(alcohol_grams - drink_data["expected_alcohol"]) < 0.1

    @pytest.mark.models
    def test_drink_zero_abv(self, db_session):
        """Test drink with zero ABV (non-alcoholic)."""
        drink = Drink(
            name="Non-Alcoholic Beer",
            abv=0.0,
            volume_ml=355,
            image_path="images/drinks/na_beer.png",
        )
        db_session.add(drink)
        db_session.commit()

        alcohol_grams = (drink.abv * drink.volume_ml * 0.789) / 100
        assert alcohol_grams == 0.0

    @pytest.mark.models
    def test_drink_high_abv(self, db_session):
        """Test drink with high ABV."""
        drink = Drink(
            name="High Proof Spirit",
            abv=95.0,
            volume_ml=30,
            image_path="images/drinks/high_proof.png",
        )
        db_session.add(drink)
        db_session.commit()

        alcohol_grams = (drink.abv * drink.volume_ml * 0.789) / 100
        # Should be a significant amount
        assert alcohol_grams > 20.0


class TestDrinkConsumptionModel:
    """Test cases for the DrinkConsumption model."""

    @pytest.mark.models
    def test_consumption_creation(self, sample_guest, sample_drink, db_session):
        """Test creating a drink consumption."""
        timestamp = datetime.utcnow()
        consumption = DrinkConsumption(
            guest_id=sample_guest.id, drink_id=sample_drink.id, timestamp=timestamp
        )
        db_session.add(consumption)
        db_session.commit()

        assert consumption.id is not None
        assert consumption.guest_id == sample_guest.id
        assert consumption.drink_id == sample_drink.id
        assert consumption.timestamp == timestamp

    @pytest.mark.models
    def test_consumption_str_representation(self, sample_consumption):
        """Test the string representation of a consumption."""
        expected = f"Consumption(Guest: {sample_consumption.guest.name}, Drink: {sample_consumption.drink.name}, Time: {sample_consumption.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
        assert str(sample_consumption) == expected

    @pytest.mark.models
    def test_consumption_relationships(self, sample_consumption):
        """Test that consumption properly links guest and drink."""
        assert sample_consumption.guest.name == "Alice"
        assert sample_consumption.drink.name == "Beer"
        assert sample_consumption.drink.abv == 5.0

    @pytest.mark.models
    def test_consumption_timestamp_ordering(self, sample_guest, db_session):
        """Test that consumptions can be ordered by timestamp."""
        beer = Drink.query.filter_by(name="Beer").first()

        # Create consumptions at different times
        base_time = datetime.utcnow()
        times = [
            base_time - timedelta(hours=2),
            base_time - timedelta(hours=1),
            base_time - timedelta(minutes=30),
            base_time,
        ]

        consumptions = []
        for i, timestamp in enumerate(times):
            consumption = DrinkConsumption(
                guest_id=sample_guest.id, drink_id=beer.id, timestamp=timestamp
            )
            db_session.add(consumption)
            consumptions.append(consumption)

        db_session.commit()

        # Query consumptions ordered by timestamp
        ordered_consumptions = (
            DrinkConsumption.query.filter_by(guest_id=sample_guest.id)
            .order_by(DrinkConsumption.timestamp)
            .all()
        )

        assert len(ordered_consumptions) == 4
        for i in range(len(ordered_consumptions) - 1):
            assert (
                ordered_consumptions[i].timestamp
                <= ordered_consumptions[i + 1].timestamp
            )


class TestModelRelationships:
    """Test cases for model relationships."""

    @pytest.mark.models
    def test_guest_consumption_drink_relationship(self, db_session):
        """Test the full relationship chain: Guest -> Consumption -> Drink."""
        # Create test data
        guest = Guest(name="Relationship Test", weight=170)
        drink = Drink(
            name="Test Drink",
            abv=6.0,
            volume_ml=330,
            image_path="images/drinks/test.png",
        )
        consumption = DrinkConsumption(
            guest_id=guest.id, drink_id=drink.id, timestamp=datetime.utcnow()
        )

        db_session.add_all([guest, drink, consumption])
        db_session.commit()

        # Test relationships
        assert len(guest.drinks) == 1
        assert guest.drinks[0].drink.name == "Test Drink"
        assert guest.drinks[0].drink.abv == 6.0

        # Test reverse relationship
        assert len(drink.consumptions) == 1
        assert drink.consumptions[0].guest.name == "Relationship Test"

    @pytest.mark.models
    def test_multiple_guests_same_drink(self, sample_drink, db_session):
        """Test multiple guests consuming the same drink."""
        guest1 = Guest(name="Guest 1", weight=150)
        guest2 = Guest(name="Guest 2", weight=160)

        db_session.add_all([guest1, guest2])
        db_session.commit()

        # Both guests drink the same beer
        consumption1 = DrinkConsumption(
            guest_id=guest1.id, drink_id=sample_drink.id, timestamp=datetime.utcnow()
        )
        consumption2 = DrinkConsumption(
            guest_id=guest2.id, drink_id=sample_drink.id, timestamp=datetime.utcnow()
        )

        db_session.add_all([consumption1, consumption2])
        db_session.commit()

        # Check that both guests have consumed the drink
        db_session.refresh(guest1)
        db_session.refresh(guest2)

        assert len(guest1.drinks) == 1
        assert len(guest2.drinks) == 1
        assert guest1.drinks[0].drink.name == "Beer"
        assert guest2.drinks[0].drink.name == "Beer"

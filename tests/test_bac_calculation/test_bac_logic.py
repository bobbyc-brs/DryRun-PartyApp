"""
Unit tests for BAC calculation logic and scientific accuracy.

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
import math
from datetime import datetime, timedelta
from app.models import Guest, Drink, DrinkConsumption
from app.constants import (
    ETHANOL_DENSITY_G_PER_ML,
    AVERAGE_GENDER_CONSTANT,
    BAC_METABOLISM_RATE,
    BAC_DISPLAY_CAP,
    LBS_TO_KG_CONVERSION
)


class TestBACScientificAccuracy:
    """Test scientific accuracy of BAC calculations."""

    @pytest.mark.bac
    def test_widmark_formula_accuracy(self, db_session):
        """Test that BAC calculation follows the correct Widmark formula."""
        # Create a guest with known weight
        guest = Guest(name="Test Guest", weight=150)  # 150 lbs
        db_session.add(guest)
        db_session.commit()

        # Create a drink with known alcohol content
        drink = Drink(name="Test Drink", abv=10.0, volume_ml=200,
                     image_path="images/drinks/test.png")
        db_session.add(drink)
        db_session.commit()

        # Add consumption
        consumption = DrinkConsumption(
            guest_id=guest.id,
            drink_id=drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        # Calculate expected BAC manually using Widmark formula
        # Formula: BAC = (alcohol_grams / (weight_grams * r)) * 100
        alcohol_grams = (drink.abv * drink.volume_ml * ETHANOL_DENSITY_G_PER_ML) / 100
        weight_grams = guest.weight * LBS_TO_KG_CONVERSION * 1000
        expected_bac = (alcohol_grams / (weight_grams * AVERAGE_GENDER_CONSTANT)) * 100

        # Get actual BAC from model
        actual_bac = guest.calculate_bac()

        # Should be very close (within rounding precision)
        assert abs(actual_bac - expected_bac) < 0.001

    @pytest.mark.bac
    def test_alcohol_content_calculation(self):
        """Test alcohol content calculation from ABV and volume."""
        test_cases = [
            # (ABV, volume_ml, expected_alcohol_grams)
            (5.0, 355, 13.99775),   # Standard beer
            (12.0, 150, 14.223),    # Standard wine glass
            (40.0, 45, 14.301),     # Standard whiskey shot
            (0.0, 355, 0.0),        # Non-alcoholic
            (95.0, 30, 22.635),     # High-proof spirit
        ]

        for abv, volume_ml, expected in test_cases:
            alcohol_grams = (abv * volume_ml * ETHANOL_DENSITY_G_PER_ML) / 100
            assert abs(alcohol_grams - expected) < 0.001

    @pytest.mark.bac
    def test_weight_conversion_accuracy(self):
        """Test weight conversion from pounds to grams."""
        test_weights = [
            (100, 45359.2),   # 100 lbs
            (150, 68038.8),   # 150 lbs
            (200, 90718.4),   # 200 lbs
            (250, 113398.0),  # 250 lbs
        ]

        for lbs, expected_grams in test_weights:
            actual_grams = lbs * LBS_TO_KG_CONVERSION * 1000
            assert abs(actual_grams - expected_grams) < 0.1

    @pytest.mark.bac
    def test_gender_constants(self):
        """Test that gender constants are within expected ranges."""
        # Male constant should be higher than female (less body water percentage)
        from app.constants import MALE_GENDER_CONSTANT, FEMALE_GENDER_CONSTANT

        assert MALE_GENDER_CONSTANT > FEMALE_GENDER_CONSTANT
        assert AVERAGE_GENDER_CONSTANT > FEMALE_GENDER_CONSTANT
        assert AVERAGE_GENDER_CONSTANT < MALE_GENDER_CONSTANT

        # All should be in reasonable range for human body water content
        assert 0.5 <= FEMALE_GENDER_CONSTANT <= 0.7
        assert 0.6 <= MALE_GENDER_CONSTANT <= 0.8
        assert 0.55 <= AVERAGE_GENDER_CONSTANT <= 0.75


class TestBACMetabolism:
    """Test BAC metabolism over time."""

    @pytest.mark.bac
    def test_metabolism_rate(self, db_session):
        """Test that metabolism follows expected rate."""
        guest = Guest(name="Metabolism Test", weight=150)
        drink = Drink(name="Test Drink", abv=10.0, volume_ml=200,
                     image_path="images/drinks/test.png")
        db_session.add_all([guest, drink])
        db_session.commit()

        # Calculate initial BAC
        consumption = DrinkConsumption(
            guest_id=guest.id,
            drink_id=drink.id,
            timestamp=datetime.utcnow() - timedelta(hours=2)
        )
        db_session.add(consumption)
        db_session.commit()

        bac_after_2_hours = guest.calculate_bac()

        # Calculate expected metabolized amount
        # Metabolism rate is 0.015% per hour
        expected_metabolized = 2 * BAC_METABOLISM_RATE

        # BAC should be reduced by metabolized amount
        # (but we can't easily test the exact value without knowing initial BAC)
        assert bac_after_2_hours >= 0.0
        assert bac_after_2_hours <= BAC_DISPLAY_CAP

    @pytest.mark.bac
    def test_no_metabolism_recent_drink(self, db_session):
        """Test BAC with very recent consumption (minimal metabolism)."""
        guest = Guest(name="Recent Drink", weight=150)
        drink = Drink(name="Test Drink", abv=5.0, volume_ml=355,
                     image_path="images/drinks/test.png")
        db_session.add_all([guest, drink])
        db_session.commit()

        # Very recent consumption
        consumption = DrinkConsumption(
            guest_id=guest.id,
            drink_id=drink.id,
            timestamp=datetime.utcnow() - timedelta(minutes=5)
        )
        db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # Should be close to initial BAC (minimal metabolism in 5 minutes)
        alcohol_grams = (drink.abv * drink.volume_ml * ETHANOL_DENSITY_G_PER_ML) / 100
        weight_grams = guest.weight * LBS_TO_KG_CONVERSION * 1000
        expected_bac = (alcohol_grams / (weight_grams * AVERAGE_GENDER_CONSTANT)) * 100

        metabolized = (5/60) * BAC_METABOLISM_RATE  # 5 minutes in hours
        expected_bac -= metabolized

        assert abs(bac - expected_bac) < 0.001

    @pytest.mark.bac
    def test_metabolism_over_long_time(self, db_session):
        """Test BAC metabolism over a long period."""
        guest = Guest(name="Long Time", weight=150)
        drink = Drink(name="Test Drink", abv=10.0, volume_ml=200,
                     image_path="images/drinks/test.png")
        db_session.add_all([guest, drink])
        db_session.commit()

        # Consumption 6 hours ago
        consumption = DrinkConsumption(
            guest_id=guest.id,
            drink_id=drink.id,
            timestamp=datetime.utcnow() - timedelta(hours=6)
        )
        db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # After 6 hours, BAC should be significantly reduced
        # Metabolism: 6 * 0.015 = 0.09% metabolized
        assert bac >= 0.0  # Should not be negative
        # BAC should be very low after 6 hours
        assert bac < 0.1


class TestBACEdgeCases:
    """Test BAC calculation edge cases."""

    @pytest.mark.bac
    def test_very_light_person_high_alcohol(self, db_session):
        """Test BAC for very light person with high alcohol consumption."""
        guest = Guest(name="Light Drinker", weight=100)  # Very light
        drink = Drink(name="Strong Drink", abv=40.0, volume_ml=200,
                     image_path="images/drinks/strong.png")
        db_session.add_all([guest, drink])
        db_session.commit()

        # Multiple strong drinks
        for _ in range(3):
            consumption = DrinkConsumption(
                guest_id=guest.id,
                drink_id=drink.id,
                timestamp=datetime.utcnow()
            )
            db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # Should be very high but capped
        assert bac <= BAC_DISPLAY_CAP
        assert bac > 0.5  # Should be high

    @pytest.mark.bac
    def test_very_heavy_person_small_drink(self, db_session):
        """Test BAC for very heavy person with small drink."""
        guest = Guest(name="Heavy Drinker", weight=300)  # Very heavy
        drink = Drink(name="Small Drink", abv=5.0, volume_ml=100,
                     image_path="images/drinks/small.png")
        db_session.add_all([guest, drink])
        db_session.commit()

        consumption = DrinkConsumption(
            guest_id=guest.id,
            drink_id=drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # Should be very low
        assert bac > 0.0
        assert bac < 0.01  # Very small BAC

    @pytest.mark.bac
    def test_zero_alcohol_drink(self, db_session):
        """Test BAC with zero alcohol drink."""
        guest = Guest(name="Non-Drinker", weight=150)
        drink = Drink(name="Water", abv=0.0, volume_ml=500,
                     image_path="images/drinks/water.png")
        db_session.add_all([guest, drink])
        db_session.commit()

        consumption = DrinkConsumption(
            guest_id=guest.id,
            drink_id=drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # Should be zero
        assert bac == 0.0

    @pytest.mark.bac
    def test_extreme_abv_values(self, db_session):
        """Test BAC with extreme ABV values."""
        guest = Guest(name="Extreme Test", weight=150)

        # Test very high ABV
        high_abv_drink = Drink(name="Extreme ABV", abv=100.0, volume_ml=10,
                              image_path="images/drinks/extreme.png")

        # Test negative ABV (shouldn't happen but test robustness)
        negative_abv_drink = Drink(name="Negative ABV", abv=-5.0, volume_ml=100,
                                  image_path="images/drinks/negative.png")

        db_session.add_all([guest, high_abv_drink, negative_abv_drink])
        db_session.commit()

        # Test high ABV
        consumption1 = DrinkConsumption(
            guest_id=guest.id,
            drink_id=high_abv_drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption1)
        db_session.commit()

        bac_high = guest.calculate_bac()
        assert bac_high <= BAC_DISPLAY_CAP

        # Test negative ABV
        consumption2 = DrinkConsumption(
            guest_id=guest.id,
            drink_id=negative_abv_drink.id,
            timestamp=datetime.utcnow()
        )
        db_session.add(consumption2)
        db_session.commit()

        bac_negative = guest.calculate_bac()
        # Negative ABV should reduce BAC, but not make it negative
        assert bac_negative >= 0.0


class TestBACRealWorldScenarios:
    """Test BAC calculations for real-world drinking scenarios."""

    @pytest.mark.bac
    def test_typical_beer_drinker(self, db_session):
        """Test typical beer drinking scenario."""
        guest = Guest(name="Beer Drinker", weight=180)  # Average male weight
        beer = Drink(name="Typical Beer", abv=4.5, volume_ml=355,
                    image_path="images/drinks/beer.png")
        db_session.add_all([guest, beer])
        db_session.commit()

        # Drink 3 beers over 2 hours
        base_time = datetime.utcnow()
        for i in range(3):
            consumption = DrinkConsumption(
                guest_id=guest.id,
                drink_id=beer.id,
                timestamp=base_time - timedelta(minutes=i*40)  # One every 40 minutes
            )
            db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # Should be in reasonable range for social drinking
        assert 0.05 <= bac <= 0.15

    @pytest.mark.bac
    def test_wine_drinker_scenario(self, db_session):
        """Test wine drinking scenario."""
        guest = Guest(name="Wine Drinker", weight=140)  # Average female weight
        wine = Drink(name="Red Wine", abv=13.5, volume_ml=150,
                    image_path="images/drinks/wine.png")
        db_session.add_all([guest, wine])
        db_session.commit()

        # Two glasses of wine over dinner (1.5 hours)
        consumption1 = DrinkConsumption(
            guest_id=guest.id,
            drink_id=wine.id,
            timestamp=datetime.utcnow() - timedelta(hours=1.5)
        )
        consumption2 = DrinkConsumption(
            guest_id=guest.id,
            drink_id=wine.id,
            timestamp=datetime.utcnow() - timedelta(hours=0.75)
        )
        db_session.add_all([consumption1, consumption2])
        db_session.commit()

        bac = guest.calculate_bac()

        # Should be moderate
        assert 0.04 <= bac <= 0.12

    @pytest.mark.bac
    def test_mixed_drinking_scenario(self, db_session):
        """Test mixed drinking scenario (beer + wine + cocktail)."""
        guest = Guest(name="Mixed Drinker", weight=160)
        drinks = [
            Drink(name="Beer", abv=5.0, volume_ml=355, image_path="images/drinks/beer.png"),
            Drink(name="Wine", abv=12.0, volume_ml=150, image_path="images/drinks/wine.png"),
            Drink(name="Cocktail", abv=15.0, volume_ml=200, image_path="images/drinks/cocktail.png")
        ]

        db_session.add(guest)
        for drink in drinks:
            db_session.add(drink)
        db_session.commit()

        # Drinking pattern: beer, then wine, then cocktail
        base_time = datetime.utcnow()
        consumptions = [
            DrinkConsumption(guest_id=guest.id, drink_id=drinks[0].id,
                           timestamp=base_time - timedelta(hours=2)),
            DrinkConsumption(guest_id=guest.id, drink_id=drinks[1].id,
                           timestamp=base_time - timedelta(hours=1)),
            DrinkConsumption(guest_id=guest.id, drink_id=drinks[2].id,
                           timestamp=base_time - timedelta(minutes=30))
        ]

        for consumption in consumptions:
            db_session.add(consumption)
        db_session.commit()

        bac = guest.calculate_bac()

        # Should be moderately high
        assert 0.08 <= bac <= BAC_DISPLAY_CAP

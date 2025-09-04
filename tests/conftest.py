"""
Pytest fixtures and configuration for Party Drink Tracker tests.

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

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from app import create_app, db
from app.models import Drink, DrinkConsumption, Guest


@pytest.fixture(scope="session")
def app():
    """Create and configure a test app instance."""
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()

    # Configure the app for testing
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Create a new database session for a test."""
    with app.app_context():
        db.create_all()

        # Create sample data
        sample_guests = [
            Guest(name="Alice", weight=150),
            Guest(name="Bob", weight=180),
            Guest(name="Charlie", weight=160),
        ]

        sample_drinks = [
            Drink(
                name="Beer", abv=5.0, volume_ml=355, image_path="images/drinks/beer.png"
            ),
            Drink(
                name="Wine",
                abv=12.0,
                volume_ml=150,
                image_path="images/drinks/wine.png",
            ),
            Drink(
                name="Whiskey",
                abv=40.0,
                volume_ml=45,
                image_path="images/drinks/whiskey.png",
            ),
        ]

        for guest in sample_guests:
            db.session.add(guest)
        for drink in sample_drinks:
            db.session.add(drink)

        db.session.commit()

        yield db.session

        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_guest(db_session):
    """Return a sample guest."""
    return Guest.query.filter_by(name="Alice").first()


@pytest.fixture
def sample_drink(db_session):
    """Return a sample drink."""
    return Drink.query.filter_by(name="Beer").first()


@pytest.fixture
def sample_consumption(sample_guest, sample_drink, db_session):
    """Create a sample drink consumption."""
    consumption = DrinkConsumption(
        guest_id=sample_guest.id, drink_id=sample_drink.id, timestamp=datetime.utcnow()
    )
    db_session.add(consumption)
    db_session.commit()
    return consumption


@pytest.fixture
def multiple_consumptions(sample_guest, db_session):
    """Create multiple drink consumptions for testing BAC calculations."""
    base_time = datetime.utcnow()

    # Create multiple drinks
    beer = Drink.query.filter_by(name="Beer").first()
    wine = Drink.query.filter_by(name="Wine").first()

    consumptions = []

    # Beer 1 hour ago
    c1 = DrinkConsumption(
        guest_id=sample_guest.id,
        drink_id=beer.id,
        timestamp=base_time - timedelta(hours=1),
    )
    db_session.add(c1)
    consumptions.append(c1)

    # Wine 30 minutes ago
    c2 = DrinkConsumption(
        guest_id=sample_guest.id,
        drink_id=wine.id,
        timestamp=base_time - timedelta(minutes=30),
    )
    db_session.add(c2)
    consumptions.append(c2)

    # Beer 10 minutes ago
    c3 = DrinkConsumption(
        guest_id=sample_guest.id,
        drink_id=beer.id,
        timestamp=base_time - timedelta(minutes=10),
    )
    db_session.add(c3)
    consumptions.append(c3)

    db_session.commit()
    return consumptions

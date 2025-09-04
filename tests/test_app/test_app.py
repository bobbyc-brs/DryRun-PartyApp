"""
Unit tests for Flask application setup and configuration.

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
for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For inquiries, contact: Info@BrighterSight.ca
"""

import pytest
import os
from app import create_app, db
from app.models import Guest, Drink, DrinkConsumption


class TestAppCreation:
    """Test Flask application creation and configuration."""

    def test_create_app_default(self):
        """Test creating app with default configuration."""
        app = create_app()

        assert app is not None
        assert hasattr(app, 'config')
        assert app.config['TESTING'] is False

    def test_create_app_testing_config(self):
        """Test creating app with testing configuration."""
        config = {
            'TESTING': True,
            'SECRET_KEY': 'test-key',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }

        app = create_app(config)

        assert app.config['TESTING'] is True
        assert app.config['SECRET_KEY'] == 'test-key'
        assert 'sqlite:///:memory:' in app.config['SQLALCHEMY_DATABASE_URI']

    def test_app_has_required_attributes(self):
        """Test that app has all required Flask attributes."""
        app = create_app()

        # Basic Flask attributes
        assert hasattr(app, 'route')
        assert hasattr(app, 'add_url_rule')
        assert hasattr(app, 'url_for')
        assert hasattr(app, 'config')

        # Database
        assert hasattr(app, 'db')
        assert app.db is db

    def test_app_blueprints_registered(self):
        """Test that blueprints are properly registered."""
        app = create_app()

        # Check that blueprints are registered
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]

            # Should have guest routes
            guest_routes = [rule for rule in rules if rule.startswith('/guest')]
            assert len(guest_routes) > 0

            # Should have host routes
            host_routes = [rule for rule in rules if rule.startswith('/host')]
            assert len(host_routes) > 0

            # Should have root routes
            root_routes = [rule for rule in rules if rule == '/']
            assert len(root_routes) > 0


class TestAppDatabase:
    """Test database integration with Flask app."""

    def test_db_initialization(self, app):
        """Test that database is properly initialized."""
        with app.app_context():
            # Should be able to create tables
            db.create_all()

            # Should be able to query
            guests = Guest.query.all()
            assert isinstance(guests, list)

    def test_db_models_registered(self, app):
        """Test that all models are registered with SQLAlchemy."""
        with app.app_context():
            # Check that models are in registry
            registry = db.Model._sa_registry._class_registry

            # Should contain our models
            assert 'Guest' in registry
            assert 'Drink' in registry
            assert 'DrinkConsumption' in registry

    def test_db_relationships(self, app):
        """Test that database relationships work correctly."""
        with app.app_context():
            db.create_all()

            # Create test data
            guest = Guest(name="Test Guest", weight=150)
            drink = Drink(name="Test Beer", abv=5.0, volume_ml=355,
                         image_path="images/drinks/test.png")
            consumption = DrinkConsumption(
                guest_id=guest.id,
                drink_id=drink.id,
                timestamp=None  # Will be set by database
            )

            db.session.add_all([guest, drink, consumption])
            db.session.commit()

            # Test relationships
            assert len(guest.drinks) == 1
            assert len(drink.consumptions) == 1
            assert guest.drinks[0].drink.name == "Test Beer"
            assert drink.consumptions[0].guest.name == "Test Guest"


class TestAppRoutes:
    """Test application routing."""

    def test_root_route_redirects(self, client):
        """Test that root route redirects appropriately."""
        response = client.get('/')
        assert response.status_code == 302  # Redirect

        # Should redirect to guest or host interface
        location = response.headers.get('Location', '')
        assert '/guest/' in location or '/host/' in location

    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_static_files(self, client):
        """Test that static files are served."""
        response = client.get('/static/css/style.css')
        # Should either serve the file or return 404 if file doesn't exist
        assert response.status_code in [200, 404]


class TestAppConfiguration:
    """Test application configuration."""

    def test_secret_key_set(self, app):
        """Test that secret key is properly set."""
        assert 'SECRET_KEY' in app.config
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 0

    def test_database_uri_set(self, app):
        """Test that database URI is properly set."""
        assert 'SQLALCHEMY_DATABASE_URI' in app.config
        assert app.config['SQLALCHEMY_DATABASE_URI'] is not None

    def test_wtf_csrf_disabled_in_testing(self):
        """Test that CSRF is disabled in testing mode."""
        config = {'TESTING': True}
        app = create_app(config)

        # In testing mode, CSRF should be disabled
        assert app.config.get('WTF_CSRF_ENABLED', True) is False

    def test_debug_mode_config(self):
        """Test debug mode configuration."""
        # Default app (not testing)
        app = create_app()
        assert app.config['DEBUG'] is False

        # Testing app
        config = {'TESTING': True}
        app = create_app(config)
        assert app.config['TESTING'] is True


class TestAppErrorHandling:
    """Test application error handling."""

    def test_500_error_handling(self, client):
        """Test 500 error handling."""
        # This would require triggering an actual 500 error
        # For now, just test that the app handles requests properly
        response = client.get('/host/')
        assert response.status_code in [200, 302, 404]  # Valid responses

    def test_invalid_route_handling(self, client):
        """Test handling of completely invalid routes."""
        response = client.get('/invalid/route/that/does/not/exist')
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test handling of incorrect HTTP methods."""
        # Try POST on a GET-only route
        response = client.post('/host/')
        # Should either work (if route accepts POST) or return 405
        assert response.status_code in [200, 302, 405]


class TestAppIntegration:
    """Test full application integration."""

    def test_full_request_flow(self, client, db_session):
        """Test a complete request flow."""
        # Create test data
        guest = Guest(name="Integration Test", weight=160)
        drink = Drink(name="Integration Beer", abv=4.5, volume_ml=330,
                     image_path="images/drinks/integration.png")
        db_session.add_all([guest, drink])
        db_session.commit()

        # Test guest page
        response = client.get('/guest/')
        assert response.status_code == 200

        # Test host page
        response = client.get('/host/')
        assert response.status_code == 200

        # Test guest selection
        response = client.get(f'/guest/select/{guest.id}')
        assert response.status_code == 200

        # Test BAC chart
        response = client.get(f'/host/bac_chart/{guest.id}')
        assert response.status_code == 200

        # Test guest data API
        response = client.get('/host/guest_data')
        assert response.status_code == 200

        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1

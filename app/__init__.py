"""
Flask application factory for the Party Drink Tracker.

This module contains the Flask application factory function that creates and configures
the Flask app instance with all necessary blueprints, database configuration, and routes.

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
from datetime import datetime

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance
db = SQLAlchemy()


def get_local_time(utc_dt):
    """
    Convert UTC datetime to local timezone for display.

    Args:
        utc_dt (datetime): UTC datetime object

    Returns:
        datetime: Local timezone datetime object
    """
    if utc_dt.tzinfo is None:
        # Assume UTC if no timezone info
        from datetime import timezone

        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    # Convert to local timezone
    local_dt = utc_dt.astimezone()
    return local_dt


def format_local_time(utc_dt, format_str="%H:%M"):
    """
    Format a UTC datetime as a local time string.

    Args:
        utc_dt (datetime): UTC datetime object
        format_str (str): Format string for strftime

    Returns:
        str: Formatted local time string
    """
    local_dt = get_local_time(utc_dt)
    return local_dt.strftime(format_str)


def create_app(config_overrides=None):
    """
    Create and configure the Flask application.

    This function creates a Flask app instance, configures it with database settings,
    registers blueprints for guest and host interfaces, and sets up root route redirects
    based on the port the application is running on.

    Args:
        config_overrides (dict, optional): Dictionary of configuration overrides

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    # Set default configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-for-party-app")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///party_drinks.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Apply configuration overrides if provided
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)

    from app.guest.routes import guest_bp
    from app.host.routes import host_bp

    app.register_blueprint(guest_bp)
    app.register_blueprint(host_bp)

    # Add root route redirects
    @app.route("/")
    def index():
        """
        Root route that redirects to the appropriate interface based on port.

        Determines whether to redirect to the guest interface (port 4000) or host
        interface (port 4001) based on the FLASK_RUN_PORT environment variable.

        Returns:
            Response: Redirect response to the appropriate dashboard.
        """
        # Check which port we're running on to determine if we're guest or host
        port = os.environ.get("FLASK_RUN_PORT", "4000")
        if port == "4001":
            return redirect(url_for("host.dashboard"))
        else:
            return redirect(url_for("guest.index"))

    with app.app_context():
        db.create_all()

    return app

"""
Guest interface routes for the Party Drink Tracker application.

This module contains all the Flask routes for the guest interface, allowing
guests to view available drinks, select drinks, and register their consumption.
The guest interface runs on port 4000 and provides a simple, user-friendly
interface for party attendees to log their drinks.

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

import pandas as pd
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app import db
from app.models import Drink, DrinkConsumption, Guest

guest_bp = Blueprint("guest", __name__, url_prefix="/guest")


@guest_bp.route("/", methods=["GET"])
def index():
    """
    Display the guest landing page with available guests and drinks.

    This route loads the guest list from ~/guest-list file and the drink list from
    ~/drinks/drink-list.csv, creating database entries for any new guests or drinks
    that don't already exist. It then renders the guest interface template.

    Returns:
        str: Rendered HTML template for the guest interface.
    """
    # Load guests from database (includes all guests, whether from file or added via web interface)
    guest_list = Guest.query.all()

    # Also ensure guests from file exist in database (for backward compatibility)
    guest_list_path = os.path.expanduser("~/guest-list")
    if os.path.exists(guest_list_path):
        with open(guest_list_path, "r") as file:
            for line in file:
                name = line.strip()
                if name:  # Skip empty lines
                    # Check if guest exists in DB, if not create
                    guest = Guest.query.filter_by(name=name).first()
                    if not guest:
                        guest = Guest(name=name)
                        db.session.add(guest)
        db.session.commit()
        # Refresh the guest list to include any newly created guests
        guest_list = Guest.query.all()

    # Read drink list from CSV
    drinks = []
    drink_list_path = os.path.expanduser("~/drinks/drink-list.csv")

    if os.path.exists(drink_list_path):
        try:
            drink_df = pd.read_csv(drink_list_path)
            for _, row in drink_df.iterrows():
                # Check if drink exists in DB, if not create
                drink = Drink.query.filter_by(name=row["name"]).first()
                if not drink:
                    image_path = f"images/drinks/{row.get('image', '')}"
                    drink = Drink(
                        name=row["name"],
                        image_path=image_path,
                        abv=float(row["abv"]),
                        volume_ml=float(row["volume_ml"]),
                    )
                    db.session.add(drink)
                drinks.append(drink)
            db.session.commit()
        except Exception as e:
            print(f"Error loading drink list: {e}")

    if not drinks:
        # If no drinks from CSV, get from DB
        drinks = Drink.query.all()

    return render_template("guest/index.html", guests=guest_list, drinks=drinks)


@guest_bp.route("/select/<int:guest_id>", methods=["GET", "POST"])
def select_guest(guest_id):
    """
    Display drink selection page for a specific guest.

    This route shows the drink selection interface for a specific guest. It handles
    both GET requests (displaying the page) and POST requests (updating guest weight).

    Args:
        guest_id (int): The ID of the guest to display the selection page for.

    Returns:
        str: Rendered HTML template for the guest's drink selection page.
    """
    guest = Guest.query.get_or_404(guest_id)
    drinks = Drink.query.all()

    if request.method == "POST":
        weight = request.form.get("weight")
        if weight:
            guest.weight = float(weight)
            db.session.commit()
            flash("Weight updated successfully!", "success")

    # Add local time formatted drink history to the template context
    from app import format_local_time

    drink_history = []
    for consumption in guest.drinks:
        drink_history.append(
            {
                "consumption": consumption,
                "local_time": format_local_time(consumption.timestamp, "%H:%M:%S"),
            }
        )

    return render_template(
        "guest/select.html", guest=guest, drinks=drinks, drink_history=drink_history
    )


@guest_bp.route("/add_guest", methods=["POST"])
def add_guest():
    """
    API endpoint to add a new guest to the system.

    This route allows creating new guests through the web interface.
    The guest will be added to the database and will appear in the guest list.

    Expected JSON payload:
        - name (str): The name of the new guest (required)
        - weight (float, optional): The weight of the guest in lbs

    Returns:
        JSON: Success/error response with guest information.
    """
    try:
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"success": False, "error": "Guest name is required"}), 400

        name = data["name"].strip()
        if not name:
            return (
                jsonify({"success": False, "error": "Guest name cannot be empty"}),
                400,
            )

        # Check if guest already exists
        existing_guest = Guest.query.filter_by(name=name).first()
        if existing_guest:
            return (
                jsonify({"success": False, "error": f'Guest "{name}" already exists'}),
                400,
            )

        # Create new guest
        weight = data.get("weight")
        if weight is not None:
            try:
                weight = float(weight)
                if weight <= 0:
                    return (
                        jsonify({"success": False, "error": "Weight must be positive"}),
                        400,
                    )
            except (ValueError, TypeError):
                return (
                    jsonify({"success": False, "error": "Invalid weight format"}),
                    400,
                )

        new_guest = Guest(name=name)
        if weight is not None:
            new_guest.weight = weight

        db.session.add(new_guest)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f'Successfully added guest "{name}"',
                "guest": {
                    "id": new_guest.id,
                    "name": new_guest.name,
                    "weight": new_guest.weight,
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@guest_bp.route("/add_drink", methods=["POST"])
def add_drink():
    """
    API endpoint to record a drink consumption for a guest.

    This endpoint creates a new DrinkConsumption record when a guest selects a drink.
    It validates that both the guest and drink exist before creating the consumption record.

    Returns:
        JSON: Success response with consumption details or error message.
    """
    guest_id = request.form.get("guest_id")
    drink_id = request.form.get("drink_id")

    if not guest_id or not drink_id:
        return jsonify({"success": False, "error": "Missing guest_id or drink_id"}), 400

    try:
        guest = Guest.query.get(guest_id)
        drink = Drink.query.get(drink_id)

        if not guest or not drink:
            return jsonify({"success": False, "error": "Guest or drink not found"}), 404

        consumption = DrinkConsumption(
            guest_id=guest_id, drink_id=drink_id, timestamp=datetime.utcnow()
        )

        db.session.add(consumption)
        db.session.commit()

        from app import format_local_time

        return jsonify(
            {
                "success": True,
                "message": f"Added {drink.name} for {guest.name}",
                "timestamp": format_local_time(consumption.timestamp, "%H:%M:%S"),
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

"""
Database models for the Party Drink Tracker application.

This module defines the SQLAlchemy models for guests, drinks, and drink consumption
tracking. It includes BAC (Blood Alcohol Content) calculation functionality using
a simplified version of the Widmark formula.

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

from datetime import datetime
from app import db
from app.constants import (
    ETHANOL_DENSITY_G_PER_ML, 
    AVERAGE_GENDER_CONSTANT, 
    BAC_METABOLISM_RATE, 
    LBS_TO_KG_CONVERSION, 
    BAC_DISPLAY_CAP, 
    BAC_DECIMAL_PRECISION
)

class Guest(db.Model):
    """
    Model representing a party guest.
    
    Attributes:
        id (int): Primary key identifier for the guest.
        name (str): The guest's name (max 100 characters).
        weight (float): The guest's weight in pounds (optional).
        drinks (relationship): One-to-many relationship with DrinkConsumption.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=True)  # in lbs
    drinks = db.relationship('DrinkConsumption', backref='consumer', lazy=True)
    
    def __repr__(self):
        """
        String representation of the Guest object.
        
        Returns:
            str: A string representation showing the guest's name.
        """
        return f"Guest('{self.name}')"
    
    def calculate_bac(self):
        """
        Calculate Blood Alcohol Content (BAC) using a simplified Widmark formula.
        
        The calculation considers:
        - Guest's weight (converted from pounds to kilograms)
        - Gender constant (assumed average for simplicity)
        - All drinks consumed and their alcohol content
        - Time elapsed since each drink consumption
        - Alcohol metabolism rate over time
        
        Returns:
            float: Current BAC as a percentage (0.0 to BAC_DISPLAY_CAP).
                  Returns 0.0 if guest has no weight or weight <= 0.
        """
        if not self.weight or self.weight <= 0:
            return 0.0
            
        # Using average gender constant for simplicity
        gender_constant = AVERAGE_GENDER_CONSTANT
        
        # Get all drinks consumed
        total_alcohol_grams = 0
        current_time = datetime.now()
        
        for consumption in self.drinks:
            drink = consumption.drink
            
            # Calculate alcohol in grams
            # ABV * volume(ml) * density of ethanol in g/ml
            alcohol_grams = drink.abv * drink.volume_ml * ETHANOL_DENSITY_G_PER_ML / 100
            
            # Calculate time elapsed in hours
            hours_elapsed = (current_time - consumption.timestamp).total_seconds() / 3600
            
            # Subtract metabolized alcohol based on metabolism rate
            # Only count what's still in system
            remaining_alcohol = max(0, alcohol_grams - (BAC_METABOLISM_RATE * hours_elapsed * self.weight * LBS_TO_KG_CONVERSION))
            total_alcohol_grams += remaining_alcohol
            
        # Convert weight from lbs to kg
        weight_kg = self.weight * LBS_TO_KG_CONVERSION
        
        # BAC = (alcohol in grams / (weight in kg * gender constant)) * 100
        bac = (total_alcohol_grams / (weight_kg * gender_constant)) * 100
        
        return round(min(bac, BAC_DISPLAY_CAP), BAC_DECIMAL_PRECISION)  # Cap BAC display and round to specified decimal places

class Drink(db.Model):
    """
    Model representing a drink type available at the party.
    
    Attributes:
        id (int): Primary key identifier for the drink.
        name (str): The drink's name (max 100 characters).
        image_path (str): Path to the drink's image file (optional).
        abv (float): Alcohol by volume percentage.
        volume_ml (float): Standard volume of the drink in milliliters.
        consumptions (relationship): One-to-many relationship with DrinkConsumption.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    abv = db.Column(db.Float, nullable=False)  # Alcohol by volume percentage
    volume_ml = db.Column(db.Float, nullable=False)  # Volume in milliliters
    consumptions = db.relationship('DrinkConsumption', backref='drink', lazy=True)
    
    def __repr__(self):
        """
        String representation of the Drink object.
        
        Returns:
            str: A string representation showing the drink's name, ABV, and volume.
        """
        return f"Drink('{self.name}', {self.abv}% ABV, {self.volume_ml}ml)"

class DrinkConsumption(db.Model):
    """
    Model representing a single drink consumption event by a guest.
    
    This model tracks when a guest consumed a specific drink, linking guests
    to drinks with a timestamp for BAC calculations.
    
    Attributes:
        id (int): Primary key identifier for the consumption record.
        guest_id (int): Foreign key reference to the Guest who consumed the drink.
        drink_id (int): Foreign key reference to the Drink that was consumed.
        timestamp (datetime): When the drink was consumed (defaults to current UTC time).
    """
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        """
        String representation of the DrinkConsumption object.
        
        Returns:
            str: A string representation showing guest ID, drink ID, and timestamp.
        """
        return f"DrinkConsumption(Guest ID: {self.guest_id}, Drink ID: {self.drink_id}, Time: {self.timestamp})"

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=True)  # in lbs
    drinks = db.relationship('DrinkConsumption', backref='consumer', lazy=True)
    
    def __repr__(self):
        return f"Guest('{self.name}')"
    
    def calculate_bac(self):
        """
        Calculate Blood Alcohol Content based on:
        - Weight
        - Gender (assumed default for simplicity)
        - Drinks consumed and their alcohol content
        - Time elapsed since consumption
        
        This is a simplified version of the Widmark formula
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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    abv = db.Column(db.Float, nullable=False)  # Alcohol by volume percentage
    volume_ml = db.Column(db.Float, nullable=False)  # Volume in milliliters
    consumptions = db.relationship('DrinkConsumption', backref='drink', lazy=True)
    
    def __repr__(self):
        return f"Drink('{self.name}', {self.abv}% ABV, {self.volume_ml}ml)"

class DrinkConsumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)
    drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"DrinkConsumption(Guest ID: {self.guest_id}, Drink ID: {self.drink_id}, Time: {self.timestamp})"

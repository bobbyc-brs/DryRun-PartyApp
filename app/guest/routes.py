"""
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

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Guest, Drink, DrinkConsumption
import os
import pandas as pd
from datetime import datetime

guest_bp = Blueprint('guest', __name__, url_prefix='/guest')

@guest_bp.route('/', methods=['GET'])
def index():
    """Guest landing page showing the list of guests and drink options"""
    # Read guest list from file
    guest_list = []
    guest_list_path = os.path.expanduser('~/guest-list')
    
    if os.path.exists(guest_list_path):
        with open(guest_list_path, 'r') as file:
            for line in file:
                name = line.strip()
                if name:  # Skip empty lines
                    # Check if guest exists in DB, if not create
                    guest = Guest.query.filter_by(name=name).first()
                    if not guest:
                        guest = Guest(name=name)
                        db.session.add(guest)
                    guest_list.append(guest)
        db.session.commit()
    else:
        # If guest list file doesn't exist, get guests from DB
        guest_list = Guest.query.all()
    
    # Read drink list from CSV
    drinks = []
    drink_list_path = os.path.expanduser('~/drinks/drink-list.csv')
    
    if os.path.exists(drink_list_path):
        try:
            drink_df = pd.read_csv(drink_list_path)
            for _, row in drink_df.iterrows():
                # Check if drink exists in DB, if not create
                drink = Drink.query.filter_by(name=row['name']).first()
                if not drink:
                    image_path = f"images/drinks/{row.get('image', '')}"
                    drink = Drink(
                        name=row['name'],
                        image_path=image_path,
                        abv=float(row['abv']),
                        volume_ml=float(row['volume_ml'])
                    )
                    db.session.add(drink)
                drinks.append(drink)
            db.session.commit()
        except Exception as e:
            print(f"Error loading drink list: {e}")
    
    if not drinks:
        # If no drinks from CSV, get from DB
        drinks = Drink.query.all()
    
    return render_template('guest/index.html', guests=guest_list, drinks=drinks)

@guest_bp.route('/select/<int:guest_id>', methods=['GET', 'POST'])
def select_guest(guest_id):
    """Page for a specific guest to select drinks"""
    guest = Guest.query.get_or_404(guest_id)
    drinks = Drink.query.all()
    
    if request.method == 'POST':
        weight = request.form.get('weight')
        if weight:
            guest.weight = float(weight)
            db.session.commit()
            flash('Weight updated successfully!', 'success')
    
    return render_template('guest/select.html', guest=guest, drinks=drinks)

@guest_bp.route('/add_drink', methods=['POST'])
def add_drink():
    """API endpoint to add a drink for a guest"""
    guest_id = request.form.get('guest_id')
    drink_id = request.form.get('drink_id')
    
    if not guest_id or not drink_id:
        return jsonify({'success': False, 'error': 'Missing guest_id or drink_id'}), 400
    
    try:
        guest = Guest.query.get(guest_id)
        drink = Drink.query.get(drink_id)
        
        if not guest or not drink:
            return jsonify({'success': False, 'error': 'Guest or drink not found'}), 404
        
        consumption = DrinkConsumption(
            guest_id=guest_id,
            drink_id=drink_id,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(consumption)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Added {drink.name} for {guest.name}',
            'timestamp': consumption.timestamp.strftime('%H:%M:%S')
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

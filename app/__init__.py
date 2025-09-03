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

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-party-app')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///party_drinks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from app.guest.routes import guest_bp
    from app.host.routes import host_bp
    
    app.register_blueprint(guest_bp)
    app.register_blueprint(host_bp)
    
    # Add root route redirects
    @app.route('/')
    def index():
        # Check which port we're running on to determine if we're guest or host
        port = os.environ.get('FLASK_RUN_PORT', '4000')
        if port == '4001':
            return redirect(url_for('host.dashboard'))
        else:
            return redirect(url_for('guest.index'))
    
    with app.app_context():
        db.create_all()
        
    return app

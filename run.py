"""
Guest interface server for the Party Drink Tracker application.

This script starts the Flask development server for the guest interface on port 4000.
Guests can access this interface to view available drinks and register their consumption.
The server runs in development mode by default with debug enabled.

Usage:
    python run.py

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
from app import create_app

# Set environment variable for port detection in routes
os.environ['FLASK_RUN_PORT'] = '4000'

app = create_app()

if __name__ == '__main__':
    # Default to development mode
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Run the guest interface on port 4000
    app.run(host='0.0.0.0', port=4000)

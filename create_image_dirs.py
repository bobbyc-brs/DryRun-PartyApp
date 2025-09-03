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

import os
from pathlib import Path

def create_image_directories():
    """Create the necessary directories for drink images"""
    # Create static/images/drinks directory
    static_drinks_dir = Path(__file__).parent / 'app' / 'static' / 'images' / 'drinks'
    if not static_drinks_dir.exists():
        static_drinks_dir.mkdir(parents=True)
        print(f"Created directory: {static_drinks_dir}")
    else:
        print(f"Directory already exists: {static_drinks_dir}")

    # Create ~/drinks directory
    home_drinks_dir = Path(os.path.expanduser('~/drinks'))
    if not home_drinks_dir.exists():
        home_drinks_dir.mkdir(parents=True)
        print(f"Created directory: {home_drinks_dir}")
    else:
        print(f"Directory already exists: {home_drinks_dir}")

if __name__ == "__main__":
    create_image_directories()
    print("Image directories created successfully!")

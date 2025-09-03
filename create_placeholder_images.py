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

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_placeholder_image(filename, text, size=(200, 200), bg_color=(240, 240, 240), text_color=(100, 100, 100)):
    """Create a simple placeholder image with text"""
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fall back to default if not available
    try:
        font = ImageFont.truetype("Arial", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    try:
        # For newer Pillow versions
        left, top, right, bottom = font.getbbox(text)
        text_width, text_height = right - left, bottom - top
    except AttributeError:
        # For older Pillow versions
        text_width, text_height = draw.textsize(text, font=font)
    
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    
    # Draw the text
    draw.text(position, text, fill=text_color, font=font)
    
    # Save the image
    img.save(filename)
    print(f"Created placeholder image: {filename}")

def create_all_placeholder_images():
    """Create placeholder images for all drinks"""
    # Define the drinks
    drinks = [
        "beer", "wine", "whiskey", "vodka", 
        "margarita", "gin_tonic", "rum_coke", "seltzer"
    ]
    
    # Create directories if they don't exist
    static_dir = Path(__file__).parent / 'app' / 'static' / 'images' / 'drinks'
    home_dir = Path(os.path.expanduser('~/drinks'))
    
    for directory in [static_dir, home_dir]:
        if not directory.exists():
            directory.mkdir(parents=True)
    
    # Create images in both locations
    for drink in drinks:
        # Create in static directory
        static_path = static_dir / f"{drink}.png"
        if not static_path.exists():
            create_placeholder_image(static_path, drink.replace('_', ' ').title())
        
        # Create in home directory
        home_path = home_dir / f"{drink}.png"
        if not home_path.exists():
            create_placeholder_image(home_path, drink.replace('_', ' ').title())

if __name__ == "__main__":
    create_all_placeholder_images()
    print("All placeholder images created successfully!")

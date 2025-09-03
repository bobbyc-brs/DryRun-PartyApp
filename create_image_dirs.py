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

import os
import csv
import shutil
from pathlib import Path
from app import create_app, db
from app.models import Guest, Drink

def create_sample_guest_list():
    """Create a sample guest list file in the home directory"""
    guest_list_path = os.path.expanduser('~/guest-list')
    
    # Check if file already exists
    if os.path.exists(guest_list_path):
        print(f"Guest list already exists at {guest_list_path}")
        return
    
    # Create sample guest list
    sample_guests = [
        "Alice",
        "Bob",
        "Charlie",
        "David",
        "Eve",
        "Frank",
        "Grace",
        "Hannah"
    ]
    
    with open(guest_list_path, 'w') as file:
        for guest in sample_guests:
            file.write(f"{guest}\n")
    
    print(f"Created sample guest list at {guest_list_path}")

def create_sample_drink_list():
    """Create a sample drink list CSV file in ~/drinks/"""
    drinks_dir = os.path.expanduser('~/drinks')
    
    # Create directory if it doesn't exist
    if not os.path.exists(drinks_dir):
        os.makedirs(drinks_dir)
    
    drink_list_path = os.path.join(drinks_dir, 'drink-list.csv')
    
    # Check if file already exists
    if os.path.exists(drink_list_path):
        print(f"Drink list already exists at {drink_list_path}")
        return
    
    # Create sample drink list
    sample_drinks = [
        {"name": "Beer", "abv": 5.0, "volume_ml": 355, "image": "beer.png"},
        {"name": "Wine", "abv": 12.0, "volume_ml": 150, "image": "wine.png"},
        {"name": "Whiskey", "abv": 40.0, "volume_ml": 45, "image": "whiskey.png"},
        {"name": "Vodka Shot", "abv": 40.0, "volume_ml": 45, "image": "vodka.png"},
        {"name": "Margarita", "abv": 15.0, "volume_ml": 200, "image": "margarita.png"},
        {"name": "Gin & Tonic", "abv": 10.0, "volume_ml": 240, "image": "gin_tonic.png"},
        {"name": "Rum & Coke", "abv": 12.0, "volume_ml": 240, "image": "rum_coke.png"},
        {"name": "Hard Seltzer", "abv": 5.0, "volume_ml": 355, "image": "seltzer.png"}
    ]
    
    with open(drink_list_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["name", "abv", "volume_ml", "image"])
        writer.writeheader()
        writer.writerows(sample_drinks)
    
    print(f"Created sample drink list at {drink_list_path}")

def copy_sample_images():
    """Create placeholder drink images"""
    try:
        from create_placeholder_images import create_all_placeholder_images
        create_all_placeholder_images()
    except ImportError:
        print("Could not import create_placeholder_images module. Using fallback method.")
        
        source_dir = Path(__file__).parent / 'app' / 'static' / 'images' / 'drinks'
        target_dir = Path(os.path.expanduser('~/drinks'))
        
        # Create directory if it doesn't exist
        if not source_dir.exists():
            source_dir.mkdir(parents=True)
        
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
        
        # For this example, we're just creating placeholder text files
        # In a real app, you would have actual image files
        sample_drinks = [
            "beer.png", "wine.png", "whiskey.png", "vodka.png", 
            "margarita.png", "gin_tonic.png", "rum_coke.png", "seltzer.png"
        ]
        
        for drink_image in sample_drinks:
            source_path = source_dir / drink_image
            target_path = target_dir / drink_image
            
            # Create empty placeholder files
            if not source_path.exists():
                with open(source_path, 'w') as f:
                    f.write(f"Placeholder for {drink_image}")
                print(f"Created placeholder for {drink_image}")
            
            # Copy to target directory
            if not target_path.exists():
                shutil.copy(source_path, target_path)
                print(f"Copied {drink_image} to {target_dir}")

def initialize_database():
    """Initialize the database with sample data"""
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have data
        if Guest.query.count() > 0 or Drink.query.count() > 0:
            print("Database already contains data. Skipping initialization.")
            return
        
        # Create sample guests
        sample_guests = [
            Guest(name="Alice", weight=130),
            Guest(name="Bob", weight=180),
            Guest(name="Charlie", weight=160),
            Guest(name="David", weight=200),
            Guest(name="Eve", weight=120),
            Guest(name="Frank", weight=190),
            Guest(name="Grace", weight=140),
            Guest(name="Hannah", weight=150)
        ]
        
        for guest in sample_guests:
            db.session.add(guest)
        
        # Create sample drinks
        sample_drinks = [
            Drink(name="Beer", abv=5.0, volume_ml=355, image_path="images/drinks/beer.png"),
            Drink(name="Wine", abv=12.0, volume_ml=150, image_path="images/drinks/wine.png"),
            Drink(name="Whiskey", abv=40.0, volume_ml=45, image_path="images/drinks/whiskey.png"),
            Drink(name="Vodka Shot", abv=40.0, volume_ml=45, image_path="images/drinks/vodka.png"),
            Drink(name="Margarita", abv=15.0, volume_ml=200, image_path="images/drinks/margarita.png"),
            Drink(name="Gin & Tonic", abv=10.0, volume_ml=240, image_path="images/drinks/gin_tonic.png"),
            Drink(name="Rum & Coke", abv=12.0, volume_ml=240, image_path="images/drinks/rum_coke.png"),
            Drink(name="Hard Seltzer", abv=5.0, volume_ml=355, image_path="images/drinks/seltzer.png")
        ]
        
        for drink in sample_drinks:
            db.session.add(drink)
        
        db.session.commit()
        print("Database initialized with sample data")

if __name__ == "__main__":
    # Create sample data files
    create_sample_guest_list()
    create_sample_drink_list()
    copy_sample_images()
    
    # Initialize the database
    initialize_database()
    
    print("Sample data initialization complete!")

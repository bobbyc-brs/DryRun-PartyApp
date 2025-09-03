#!/usr/bin/env python
"""Cleanup script to remove generated data files"""

import os
import shutil
from pathlib import Path
import sys

def main():
    """Main cleanup function"""
    print("Party Drink Tracker Cleanup Utility")
    print("==================================")
    print("This will remove all generated data files, including:")
    print("  - ~/guest-list")
    print("  - ~/drinks/ directory and contents")
    print("  - SQLite database file")
    print()
    
    confirm = input("Are you sure you want to proceed? (y/n): ").lower()
    if confirm != 'y':
        print("Cleanup cancelled.")
        return
    
    # Remove guest list
    guest_list_path = os.path.expanduser('~/guest-list')
    if os.path.exists(guest_list_path):
        os.remove(guest_list_path)
        print(f"Removed {guest_list_path}")
    
    # Remove drinks directory
    drinks_dir = Path(os.path.expanduser('~/drinks'))
    if drinks_dir.exists():
        shutil.rmtree(drinks_dir)
        print(f"Removed {drinks_dir}")
    
    # Remove database file
    project_dir = Path(__file__).parent.absolute()
    db_file = project_dir / 'instance' / 'party_drinks.db'
    if db_file.exists():
        os.remove(db_file)
        print(f"Removed {db_file}")
    
    # Remove __pycache__ directories
    for pycache_dir in project_dir.glob('**/__pycache__'):
        shutil.rmtree(pycache_dir)
        print(f"Removed {pycache_dir}")
    
    print("\nCleanup complete! You can now run init_sample_data.py to recreate the sample data.")

if __name__ == "__main__":
    main()

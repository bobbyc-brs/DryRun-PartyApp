"""
Setup script for the Party Drink Tracker application.

This script automates the initial setup process for the Party Drink Tracker,
including virtual environment creation, dependency installation, and sample
data initialization. It provides an interactive setup experience for new users.

Usage:
    python setup.py

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

#!/usr/bin/env python

import os
import subprocess
import sys
from pathlib import Path

def main():
    """
    Main setup function for the Party Drink Tracker application.
    
    This function handles the complete setup process including:
    - Virtual environment creation (if not already in one)
    - Dependency installation from requirements.txt
    - Directory structure creation
    - Sample data initialization
    
    The function provides interactive prompts for virtual environment creation
    and gives clear instructions for next steps after setup completion.
    """
    project_dir = Path(__file__).parent.absolute()
    
    print("Setting up Party Drink Tracker...")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\nWARNING: You are not running in a virtual environment!")
        create_venv = input("Would you like to create a virtual environment? (y/n): ").lower()
        
        if create_venv == 'y':
            print("\nCreating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=project_dir, check=True)
            
            # Determine the activate script based on platform
            if sys.platform == 'win32':
                activate_script = os.path.join(project_dir, "venv", "Scripts", "activate")
                print(f"\nVirtual environment created! Activate it with:\n{activate_script}")
            else:
                activate_script = os.path.join(project_dir, "venv", "bin", "activate")
                print(f"\nVirtual environment created! Activate it with:\nsource {activate_script}")
                
            print("\nAfter activating, run this script again to install dependencies.")
            return
        else:
            print("\nContinuing without virtual environment...")
    
    # Install requirements
    print("\nInstalling dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=project_dir, check=True)
    
    # Create directories and sample data
    print("\nSetting up directories and sample data...")
    subprocess.run([sys.executable, "create_image_dirs.py"], cwd=project_dir, check=True)
    subprocess.run([sys.executable, "create_placeholder_images.py"], cwd=project_dir, check=True)
    subprocess.run([sys.executable, "init_sample_data.py"], cwd=project_dir, check=True)
    
    print("\nSetup complete! You can now run the application with:")
    print("  - Guest interface (port 4000): python run.py")
    print("  - Host interface (port 4001): python run_host.py")
    print("  - Or use the start_servers.sh script to run both simultaneously")

if __name__ == "__main__":
    main()

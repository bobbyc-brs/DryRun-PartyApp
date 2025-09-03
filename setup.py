#!/usr/bin/env python
"""Setup script for Party Drink Tracker"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Main setup function"""
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

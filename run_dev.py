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

#!/usr/bin/env python
"""Development script to run both guest and host servers"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

def run_server(script_path, port):
    """Run a server script in a subprocess"""
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = 'True'
    
    subprocess.run([sys.executable, script_path], env=env)

def open_browser(port, delay=2):
    """Open browser after a delay"""
    def _open_browser():
        time.sleep(delay)
        webbrowser.open(f'http://localhost:{port}')
    
    thread = threading.Thread(target=_open_browser)
    thread.daemon = True
    thread.start()

def main():
    """Main function to run both servers"""
    project_dir = Path(__file__).parent.absolute()
    guest_script = project_dir / 'run.py'
    host_script = project_dir / 'run_host.py'
    
    print("Starting Party Drink Tracker in development mode...")
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\nWARNING: You are not running in a virtual environment!")
        print("It's recommended to activate the virtual environment first.")
        continue_anyway = input("Continue anyway? (y/n): ").lower()
        if continue_anyway != 'y':
            print("Exiting...")
            return
    
    # Check if sample data exists
    guest_list_path = os.path.expanduser('~/guest-list')
    drink_list_path = os.path.expanduser('~/drinks/drink-list.csv')
    
    if not os.path.exists(guest_list_path) or not os.path.exists(drink_list_path):
        print("\nSample data files not found. Running initialization script...")
        subprocess.run([sys.executable, 'init_sample_data.py'], cwd=project_dir, check=True)
    
    # Create placeholder images if needed
    drinks_dir = Path(os.path.expanduser('~/drinks'))
    if not any(drinks_dir.glob('*.png')):
        print("\nCreating placeholder drink images...")
        subprocess.run([sys.executable, 'create_placeholder_images.py'], cwd=project_dir, check=True)
    
    # Start servers in separate threads
    print("\nStarting guest server on port 4000...")
    guest_thread = threading.Thread(target=run_server, args=(guest_script, 4000))
    guest_thread.daemon = True
    guest_thread.start()
    
    print("Starting host server on port 4001...")
    host_thread = threading.Thread(target=run_server, args=(host_script, 4001))
    host_thread.daemon = True
    host_thread.start()
    
    # Open browsers
    print("\nOpening browsers...")
    open_browser(4000)
    open_browser(4001, delay=3)
    
    print("\nServers are running!")
    print("Guest interface: http://localhost:4000")
    print("Host interface: http://localhost:4001")
    print("\nPress Ctrl+C to stop the servers")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()

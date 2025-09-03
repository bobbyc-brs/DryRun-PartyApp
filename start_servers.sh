#!/bin/bash

# Exit on error
set -e

# Change to the project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating image directories..."
python create_image_dirs.py

# Initialize sample data if needed
echo "Initializing sample data..."
python init_sample_data.py

# Start the servers
echo "Starting servers..."
echo "Guest interface will be available at http://localhost:4000"
echo "Host interface will be available at http://localhost:4001"
echo ""
echo "Press Ctrl+C to stop the servers"

# Start the guest server in the background
python run.py &
GUEST_PID=$!

# Start the host server in the background
python run_host.py &
HOST_PID=$!

# Function to kill servers on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $GUEST_PID $HOST_PID 2>/dev/null || true
    exit 0
}

# Register the cleanup function for when the script is interrupted
trap cleanup INT TERM

# Wait for both processes
wait

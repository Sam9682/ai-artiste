#!/bin/bash
# Start script for Artist-Venue Matching Platform

echo "Starting Artist-Venue Matching Platform..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
    exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000
else
    echo "Running locally"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Start server
    echo "Starting server on http://localhost:8000"
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
fi

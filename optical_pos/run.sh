#!/bin/bash
# This script sets up the environment and runs the Optical POS application on macOS/Linux.

echo "--- Setting up Python virtual environment... ---"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment. Please ensure python3 is installed."
        exit 1
    fi
fi

source .venv/bin/activate

echo "--- Installing dependencies from requirements.txt... ---"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo "--- Starting Optical POS Application... ---"
python app.py

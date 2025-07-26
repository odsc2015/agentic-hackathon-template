#!/bin/bash
set -e

echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r ./backend/requirements.txt

echo "Setup complete!"

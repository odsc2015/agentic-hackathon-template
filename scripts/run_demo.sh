#!/bin/bash
set -e

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting FastAPI demo app..."
uvicorn ./backend/main:app --reload --host 0.0.0.0 --port 8080

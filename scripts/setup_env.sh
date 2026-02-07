#!/bin/bash
set -e

echo "======================================="
echo " Vidhi Setup: Creating Virtual Env"
echo "======================================="

python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup complete."
echo "To activate env later, run:"
echo "source .venv/bin/activate"

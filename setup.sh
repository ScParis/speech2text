#!/bin/bash

# Define the virtual environment path
VENV_PATH="venv"

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-pyaudio \
    ffmpeg \
    portaudio19-dev \
    python3-dev

# Install Python dependencies
pip install -r requirements.txt

# Verify installations
echo "Installation complete. Dependencies:"
pip list

# Deactivate virtual environment
deactivate

echo "Setup complete. Activate the virtual environment with 'source venv/bin/activate' before running the app."

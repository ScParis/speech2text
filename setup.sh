#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

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

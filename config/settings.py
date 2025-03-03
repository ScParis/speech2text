import os
import json
import logging
from pathlib import Path

# Configurações básicas
APP_NAME = "Speech to Text Transcriber"
VERSION = "1.0.0"
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output_files"
CONFIG_DIR = BASE_DIR / "config"
USER_CONFIG_FILE = CONFIG_DIR / "user_config.json"

# Configurações de áudio
AUDIO_CONFIG = {
    "chunk_size": 1024,
    "format": "paInt16",
    "channels": 1,
    "rate": 8000,
    "record_seconds": 1
}

# Configurações da API Gemini
API_CONFIG = {
    "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash",
    "max_retries": 3,
    "timeout": 30,
    "chunk_size_mb": 15
}

# ...existing code for API key management...

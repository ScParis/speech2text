import os
import logging
import json
from pathlib import Path
from python_dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações básicas
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output_files"
CONFIG_FILE = BASE_DIR / "config" / "user_config.json"

def save_api_key(api_key):
    """Salva a chave API do usuário"""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"GEMINI_API_KEY": api_key}, f)

def load_api_key():
    """Carrega a chave API do usuário"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("GEMINI_API_KEY")
    except Exception as e:
        logging.error(f"Erro ao carregar configuração: {e}")
    return None

# Configurações de áudio
AUDIO_CONFIG = {
    "CHUNK": 1024,
    "FORMAT": "paInt16",
    "CHANNELS": 1,
    "RATE": 8000,
    "RECORD_SECONDS": 1
}

# Configurações da API
GEMINI_API_KEY = load_api_key()  # Pode ser None inicialmente
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent'

# Configurações da requisição Gemini
GEMINI_CONFIG = {
    "max_retries": 3,
    "timeout": 60,
    "chunk_size_mb": 10,
    "max_workers": 2,
    "headers": {
        "Content-Type": "application/json"
    }
}

# Atualizar headers se a chave API existir
if GEMINI_API_KEY:
    GEMINI_CONFIG["headers"]["x-goog-api-key"] = GEMINI_API_KEY

def update_api_key(api_key):
    """Atualiza a chave API nas configurações"""
    global GEMINI_API_KEY
    GEMINI_API_KEY = api_key
    GEMINI_CONFIG["headers"]["x-goog-api-key"] = api_key
    save_api_key(api_key)

def setup_logging():
    """Configura o logging do sistema"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(OUTPUT_DIR, 'speech_to_text.log')),
            logging.StreamHandler()
        ]
    )

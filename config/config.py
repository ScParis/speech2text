import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações básicas
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output_files"

# Configurações de áudio
AUDIO_CONFIG = {
    "CHUNK": 1024,
    "FORMAT": "paInt16",
    "CHANNELS": 1,
    "RATE": 8000,
    "RECORD_SECONDS": 1
}

# Configurações da API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Removido o 'VS' do final
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent'

# Verificação da chave API
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")

# Configurações da requisição Gemini
GEMINI_CONFIG = {
    "max_retries": 3,
    "timeout": 60,
    "chunk_size_mb": 10,
    "max_workers": 2,  # Adicionado número de workers para processamento paralelo
    "headers": {
        "Content-Type": "application/json",
        "x-goog-api-key": os.getenv('GEMINI_API_KEY')
    }
}

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

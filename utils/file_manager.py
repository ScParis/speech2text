import os
import shutil
import logging
from pathlib import Path
from config.config import OUTPUT_DIR

def clear_output_directory():
    """
    Remove todos os arquivos do diretório de saída.
    """
    try:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)  # Remove o diretório e seu conteúdo
        os.makedirs(OUTPUT_DIR)        # Recria o diretório
        logging.info(f"Diretório de saída limpo: {OUTPUT_DIR}")
    except Exception as e:
        logging.error(f"Erro ao limpar diretório de saída: {e}")

def ensure_directory_exists(directory):
    """
    Garante que um diretório existe, criando-o se necessário.
    """
    os.makedirs(directory, exist_ok=True)

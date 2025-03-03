import os
import wave
import math
from pydub import AudioSegment
import logging
from config.config import OUTPUT_DIR

def split_audio(input_file, max_size_mb=15):
    """
    Divide um arquivo de áudio em partes menores
    """
    try:
        # Carregar o áudio
        audio = AudioSegment.from_file(input_file)
        
        # Calcular duração total em milissegundos
        duration_ms = len(audio)
        
        # Estimar o tamanho por minuto
        size_bytes = os.path.getsize(input_file)
        bytes_per_ms = size_bytes / duration_ms
        
        # Calcular a duração máxima por chunk para ficar dentro do limite
        max_size_bytes = max_size_mb * 1024 * 1024  # Converter MB para bytes
        chunk_duration = math.floor(max_size_bytes / bytes_per_ms)
        
        chunks = []
        for start in range(0, duration_ms, chunk_duration):
            # Extrair chunk do áudio
            end = min(start + chunk_duration, duration_ms)
            chunk = audio[start:end]
            
            # Salvar chunk
            chunk_path = os.path.join(OUTPUT_DIR, f"chunk_{len(chunks)}.wav")
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
            
        return chunks
    except Exception as e:
        logging.error(f"Erro ao dividir áudio: {e}")
        return []

def combine_texts(texts):
    """
    Combina múltiplos textos em um só
    """
    return " ".join(text for text in texts if text)

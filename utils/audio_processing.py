import os
import math
from pydub import AudioSegment
import logging
from config.config import OUTPUT_DIR

def split_audio_file(input_file, max_size_mb=15):
    """Divide um arquivo de áudio em partes menores que o limite da API"""
    try:
        # Carregar o áudio
        audio = AudioSegment.from_file(input_file)
        
        # Reduzir qualidade do áudio antes de dividir
        audio = audio.set_frame_rate(16000)  # Reduzir taxa de amostragem
        audio = audio.set_channels(1)        # Converter para mono
        
        # Calcular duração total em milissegundos
        duration_ms = len(audio)
        
        # Calcular número de chunks baseado no tamanho alvo
        target_size = 15 * 1024 * 1024  # 15MB em bytes (com margem de segurança)
        chunk_size_estimate = os.path.getsize(input_file) / duration_ms
        chunk_duration = int((target_size / chunk_size_estimate) * 0.8)  # 20% de margem
        
        chunks = []
        for start in range(0, duration_ms, chunk_duration):
            # Extrair chunk
            end = min(start + chunk_duration, duration_ms)
            chunk = audio[start:end]
            
            # Aplicar compressão adicional
            chunk = chunk.set_frame_rate(16000)  # Reduzir taxa de amostragem
            chunk = chunk.set_channels(1)        # Garantir áudio mono
            
            # Salvar com alta compressão
            chunk_path = os.path.join(OUTPUT_DIR, f"chunk_{len(chunks)}.wav")
            chunk.export(
                chunk_path,
                format="wav",
                parameters=[
                    "-ar", "16000",     # Taxa de amostragem
                    "-ac", "1",         # Mono
                    "-b:a", "64k",      # Bitrate mais baixo
                    "-compression_level", "8"  # Máxima compressão
                ]
            )
            
            # Verificar tamanho final
            if os.path.getsize(chunk_path) > target_size:
                logging.warning(f"Chunk {len(chunks)} ainda grande, aplicando compressão adicional...")
                chunk.export(
                    chunk_path,
                    format="wav",
                    parameters=[
                        "-ar", "16000",
                        "-ac", "1",
                        "-b:a", "48k",   # Bitrate ainda mais baixo
                        "-compression_level", "10"
                    ]
                )
            
            chunks.append(chunk_path)
            
        logging.info(f"Áudio dividido em {len(chunks)} partes")
        return chunks
        
    except Exception as e:
        logging.error(f"Erro ao dividir áudio: {e}")
        return None

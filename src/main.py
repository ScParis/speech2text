import os
import sys
import logging
from services.audio_service import extract_audio_from_video

# Adiciona o diretório raiz ao PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.audio_service import (
    record_audio,
    download_audio_from_youtube,
    download_tiktok_video,
    download_instagram_story
)
from services.transcription_service import (
    process_transcription, 
    improve_transcript,
    process_and_analyze_transcription  # Adicionada nova importação
)
from utils.validators import (
    validate_audio_file,
    validate_video_file,
    identify_platform
)
from utils.file_manager import clear_output_directory
from config.config import setup_logging, OUTPUT_DIR  # Adicionado OUTPUT_DIR

# Setup inicial
setup_logging()
clear_output_directory()

def main():
    """Função principal para iniciar o processo."""
    global continue_processing
    continue_processing = True

    while continue_processing:
        # Menu de opções
        logging.info("\nEscolha uma opção de entrada:")
        logging.info("1. Gravação de voz")
        logging.info("2. Envio de arquivo (áudio ou vídeo)")
        logging.info("3. Envio de link")

        opcao = input("\nDigite 1, 2 ou 3: ").strip()

        if opcao == "1":
            audio_file = record_audio()
            if audio_file:
                process_and_show_results(audio_file)
        
        elif opcao == "2":
            file_path = input("Digite o caminho completo para o arquivo: ").strip()
            if validate_audio_file(file_path) or validate_video_file(file_path):
                process_and_show_results(file_path)
            else:
                logging.error("Arquivo inválido.")
        
        elif opcao == "3":
            url = input("Digite a URL da plataforma: ").strip()
            platform = identify_platform(url)
            if platform:
                try:
                    audio_file = download_and_process_url(url, platform)
                    if audio_file:
                        process_and_show_results(audio_file)
                except Exception as e:
                    logging.error(f"Erro ao processar URL: {e}")
            else:
                logging.error("URL não suportada.")
        
        else:
            logging.error("Opção inválida.")

        continue_processing = input("\nDeseja realizar novo envio (s/n)? ").lower().strip() == 's'

def process_and_show_results(audio_file):
    """Processa o arquivo de áudio e mostra os resultados."""
    try:
        transcricao, transcricao_melhorada, analise = process_and_analyze_transcription(audio_file)
        
        if transcricao:
            print("\nTranscrição original:")
            print(transcricao)
            
        if transcricao_melhorada:
            print("\nTranscrição melhorada:")
            print(transcricao_melhorada)
            
        if analise:
            print("\nAnálise e Percepções:")
            print(analise)
        
    except Exception as e:
        logging.error(f"Erro ao processar arquivo: {e}")

def download_and_process_url(url, platform):
    """Baixa e processa áudio/vídeo de uma URL."""
    try:
        if platform == "YouTube":
            audio_file, error = download_audio_from_youtube(url)
            if error:
                logging.error(f"Erro no download: {error}")
                return None
            if audio_file and os.path.exists(audio_file):
                return audio_file
            logging.error("Arquivo de áudio não encontrado após download")
            return None
        elif platform == "TikTok":
            video_file, error = download_tiktok_video(url)
            if error:
                logging.error(f"Erro no download: {error}")
                return None
            if video_file:
                audio_file, error = extract_audio_from_video(video_file, os.path.join(OUTPUT_DIR, "audio.wav"))
                if error:
                    logging.error(f"Erro na extração: {error}")
                    return None
                return audio_file
        elif platform in ["Instagram Story", "Instagram Reel"]:
            video_file, error = download_instagram_story(url)
            if error:
                logging.error(f"Erro no download: {error}")
                return None
            if video_file:
                audio_file, error = extract_audio_from_video(video_file, os.path.join(OUTPUT_DIR, "audio.wav"))
                if error:
                    logging.error(f"Erro na extração: {error}")
                    return None
                return audio_file
        return None
    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        return None

if __name__ == '__main__':
    main()

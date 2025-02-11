import requests
import json
import pyaudio
import wave
import os
import google.auth
import base64
import yt_dlp as youtube_dl  # Usar yt-dlp
from config import GEMINI_API_KEY, GEMINI_API_URL  # Importar as variáveis do config.py
import subprocess
import time  # Para medir o tempo
import tqdm  # Para a barra de progresso
import re #para validar a URL
import shutil
from urllib.parse import urlparse, parse_qs
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("output_files", 'speech_to_text.log')),
        logging.StreamHandler()
    ]
)

# Configurações de gravação
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000 #ALTERADO - REDUZIR A TAXA DE AMOSTRAGEM
RECORD_SECONDS = 1  # Grava por 5 segundos

OUTPUT_DIR = "output_files"  # Define your output directory

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WAVE_OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, "output.wav")
MP3_OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, "output.mp3")
WAVE_OUTPUT_FILENAME_REDUCED = os.path.join(OUTPUT_DIR, "output_reduced.wav")

# Configurações da API Gemini (Carregadas do config.py)
GEMINI_API_URL = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}" # Usar a variável GEMINI_API_URL do config.py

class MyLogger(object):
    def __init__(self):
        self.pbar = None

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        logging.error(msg)

    def info(self, msg):
        if msg.startswith('[download]'):
            if self.pbar is None:
                self.pbar = tqdm.tqdm(total=100, unit="%", desc="Baixando")
            percentage = float(msg.split()[1][:-1])
            self.pbar.update(percentage - (self.pbar.n or 0))
            if percentage >= 100:
                self.pbar.close()
                self.pbar = None

def record_audio():
    """Grava áudio do microfone e salva em um arquivo."""
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(WAVE_OUTPUT_FILENAME)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        logging.info("Iniciando gravação de áudio...")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        logging.info("Gravação de áudio concluída.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return WAVE_OUTPUT_FILENAME
    except Exception as e:
        logging.error(f"Erro durante a gravação de áudio: {e}")
        return None

def download_audio_from_youtube(youtube_url, output_filename="youtube_audio.webm"):
    """Baixa o áudio de um vídeo do YouTube e salva em um arquivo WEBM."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_filename,
            'extractaudio': True,
            'audioformat': 'webm',
            'noplaylist': True,
            'logger': MyLogger(),
            'progress_hooks': [],
            'quiet': True,
            'force': True,
            'no_warnings': True,
        }
        start_time_download = time.time()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        download_time = time.time() - start_time_download
        logging.info(f"Download de áudio do YouTube concluído em {download_time:.2f} segundos")
        return output_filename, download_time
    except Exception as e:
        logging.error(f"Erro ao baixar o áudio do YouTube: {e}")
        return None, None

def clear_output_directory(max_files=10):
    """
    Remove arquivos antigos do diretório de saída.
    Mantém os últimos 'max_files' arquivos.
    """
    try:
        files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) 
                 if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
        
        # Ordenar arquivos por data de modificação
        files.sort(key=os.path.getmtime, reverse=True)
        
        # Excluir arquivos extras
        for file in files[max_files:]:
            try:
                os.unlink(file)
                logging.info(f"Arquivo antigo removido: {file}")
            except Exception as e:
                logging.warning(f"Não foi possível remover {file}: {e}")
    except Exception as e:
        logging.error(f"Erro ao limpar diretório de saída: {e}")

def is_valid_youtube_url(url):
    """
    Valida se a URL é de um vídeo do YouTube, incluindo variações como:
    - Links curtos (youtu.be)
    - Links com parâmetros de compartilhamento
    - Links do YouTube Music
    - Links com timestamp
    """
    youtube_regex_patterns = [
        # Padrão completo do YouTube
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})',
        
        # Links curtos do YouTube (youtu.be)
        r'https?://(?:www\.)?youtu\.be/([^&\?]+)',
        
        # Links do YouTube Music
        r'(https?://)?(music\.youtube\.com)/(watch\?v=|embed/|v/)?([^&=%\?]{11})',
        
        # Links com parâmetros adicionais
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/)?([^&=%\?]{11})(\?.*)?'
    ]
    
    for pattern in youtube_regex_patterns:
        match = re.match(pattern, url)
        if match:
            return True
    return False

def extract_video_id(url):
    """
    Extrai o ID do vídeo do YouTube de diferentes formatos de URL, 
    incluindo links com parâmetros de compartilhamento e timestamp.
    """
    # Padrões para diferentes tipos de URLs do YouTube
    youtube_patterns = [
        # Padrão completo do YouTube
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\?]+)',
        
        # Links curtos do YouTube (youtu.be)
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^&\?\s]+)',
        
        # YouTube Music
        r'(?:https?:\/\/)?music\.youtube\.com\/watch\?v=([^&\?]+)',
        
        # Links com parâmetros adicionais (si, t, etc)
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\?\s]+)'
    ]
    
    # Tenta casar com cada padrão
    for pattern in youtube_patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            
            # Remove qualquer parâmetro adicional após o ID do vídeo
            video_id = video_id.split('&')[0].split('?')[0]
            
            return video_id
    
    # Se nenhum padrão funcionar
    logging.warning(f"Não foi possível extrair o ID do vídeo da URL: {url}")
    return None

def reduce_sample_rate(input_file, output_file, new_rate):
    """Reduz a taxa de amostragem de um arquivo de áudio usando ffmpeg."""
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(input_file):
            logging.error(f"Erro: Arquivo não encontrado: {input_file}")
            return None, None

        start_time_conversion = time.time()
        subprocess.run([
            "ffmpeg",
            "-i", input_file,
            "-ar", str(new_rate),
            output_file
        ], check=True, capture_output=True, text=True, timeout=600) # Limite de tempo de 10 minutos
        return output_file, time.time() - start_time_conversion
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao reduzir a taxa de amostragem: {e.stderr}")
        return None, None
    except subprocess.TimeoutExpired:
        logging.error("Tempo limite excedido ao reduzir a taxa de amostragem.")
        return None, None
    except FileNotFoundError:
        logging.error("Erro: ffmpeg não encontrado. Certifique-se de que o ffmpeg está instalado e acessível através da linha de comando.")
        return None, None

def convert_to_mp3(input_file, output_file):
    """Converte um arquivo de áudio para MP3 usando ffmpeg."""
    try:
        start_time_conversion = time.time()
        subprocess.run([
            "ffmpeg",
            "-i", input_file,
            "-vn",  # Sem vídeo
            "-acodec", "libmp3lame",  # Codec MP3
            "-ab", "64k",  # Bitrate 64kbps
            output_file
        ], check=True, capture_output=True, text=True, timeout=600) # Limite de tempo de 10 minutos
        return output_file, time.time() - start_time_conversion
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao converter para MP3: {e.stderr}")
        return None, None
    except subprocess.TimeoutExpired:
        logging.error("Tempo limite excedido ao converter para MP3.")
        return None, None
    except FileNotFoundError:
        logging.error("Erro: ffmpeg não encontrado. Certifique-se de que o ffmpeg está instalado e acessível através da linha de comando.")
        return None, None

def correct_transcript_gemini(transcript):
    """Corrigir a transcrição com o Gemini."""
    prompt = f"""Corrija a ortografia e gramática do texto a seguir. Certifique-se de que o nome da empresa seja sempre "PipeRun", e não "Papurã" ou qualquer outra variação.
    {transcript}
    """
    corrected_transcript = generate_text_gemini(prompt)

    if corrected_transcript:
        return corrected_transcript
    else:
        logging.error("Falha ao corrigir a transcrição com o Gemini.")
        return transcript

def transcribe_audio_gemini(audio_file):
    """Transcreve um arquivo de áudio usando a API Gemini."""
    try:
        with open(audio_file, "rb") as f:
            audio_data = f.read()

        # Codifica o áudio em Base64
        audio_encoded = base64.b64encode(audio_data).decode("utf-8")

        #TAMANHO DO ARQUIVO
        tamanho_audio = len(audio_encoded)
        # print(f"Tamanho dos dados de áudio codificados em Base64: {tamanho_audio} bytes")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": """Transcreva o áudio completo a seguir para texto. Separe o diálogo por locutor e interlocutor, indicando quem fala o quê. Se tiver dificuldade em entender alguma palavra, tente aproximar ao máximo. Não adicione informações que não estão presentes no áudio.""" # PROMPT DETALHADO
                        },
                        {
                            "inlineData": {
                                "mimeType": "audio/mp3",  # Ajuste o mimeType se necessário
                                "data": audio_encoded
                            }
                        }
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        # print("Payload JSON:", json.dumps(payload))  # Removido para reduzir a saída
        start_time_transcription = time.time()
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        transcription_time = time.time() - start_time_transcription
        #print("Resposta da API Gemini:", response.text) # Removido para reduzir a saída

        response.raise_for_status()

        result = response.json()

        # Extrai o texto gerado da resposta
        try:
            transcript = result["candidates"][0]["content"]["parts"][0]["text"]
            return transcript, transcription_time
        except (KeyError, IndexError):
            logging.error("Erro ao extrair a transcrição da resposta do Gemini.")
            logging.error("Resposta completa do Gemini:", result)
            return None, None

    except FileNotFoundError:
        logging.error(f"Erro: Arquivo não encontrado: {audio_file}")
        return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição para a API Gemini: {e}")
        return None, None
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar a resposta JSON da API Gemini: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Erro geral na transcrição com Gemini: {e}")
        return None, None

def generate_text_gemini(prompt):
    """Gera texto usando a API Gemini (para aprimoramento, se necessário)."""
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        result = response.json()
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            logging.error("Erro ao extrair o texto da resposta da API Gemini.")
            logging.error("Resposta completa do Gemini:", result)
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição à API Gemini: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar a resposta JSON da API Gemini: {e}")
        return None

if __name__ == "__main__":
    clear_output_directory()  # Limpar diretório de saída no início

    # Função para solicitar entrada do usuário com validação
    def get_user_input(prompt, validation_func=None, error_message=None):
        while True:
            user_input = input(prompt).strip()
            
            # Se nenhuma função de validação for fornecida, aceita qualquer entrada não vazia
            if not validation_func:
                if user_input:
                    return user_input
                print("Entrada inválida. Por favor, tente novamente.")
            else:
                # Se a função de validação for fornecida, usa-a para validar
                if validation_func(user_input):
                    return user_input
                
                # Mensagem de erro personalizada ou padrão
                print(error_message or "Entrada inválida. Por favor, tente novamente.")

    # Menu de opções com mais flexibilidade
    logging.info("Escolha uma opção de entrada de áudio:")
    logging.info("1. Gravar áudio do microfone")
    logging.info("2. Carregar arquivo de áudio local")
    logging.info("3. Baixar áudio do YouTube (vídeo, música, shorts)")
    
    # Solicitar opção com validação
    opcao = get_user_input(
        "Digite 1, 2 ou 3: ", 
        validation_func=lambda x: x in ['1', '2', '3'],
        error_message="Por favor, escolha 1, 2 ou 3."
    )

    # Variável para armazenar o caminho do arquivo de áudio
    audio_file = None

    if opcao == "1":
        # Gravação de áudio do microfone
        logging.info("Preparando para gravar. Certifique-se de que o microfone está conectado.")
        start_time = time.time()
        audio_file = record_audio()
        
        if not audio_file:
            logging.error("Falha na gravação de áudio. Saindo.")
            exit(1)
        
        record_time = time.time() - start_time
        logging.info(f"Áudio gravado e salvo em {audio_file} em {record_time:.2f} segundos")

    elif opcao == "2":
        # Carregar arquivo de áudio local com validação de existência
        def validate_audio_file(file_path):
            # Extensões de áudio comuns
            audio_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.webm']
            return (
                os.path.isfile(file_path) and 
                any(file_path.lower().endswith(ext) for ext in audio_extensions)
            )

        audio_file = get_user_input(
            "Digite o caminho completo para o arquivo de áudio: ", 
            validation_func=validate_audio_file,
            error_message="Arquivo de áudio inválido ou não encontrado. Verifique o caminho e a extensão."
        )
        logging.info(f"Arquivo de áudio especificado: {audio_file}")

    elif opcao == "3":
        # Download de áudio do YouTube com suporte a diferentes URLs
        youtube_url = get_user_input(
            "Digite o link do YouTube (vídeo, música, shorts): ", 
            validation_func=is_valid_youtube_url,
            error_message="URL do YouTube inválida. Verifique o link."
        )

        # Extrair ID do vídeo
        video_id = extract_video_id(youtube_url)
        
        if not video_id:
            logging.error("Não foi possível extrair o ID do vídeo. Saindo.")
            exit(1)

        # Reconstruir URL canônica
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        logging.info(f"URL do YouTube processada: {youtube_url}")

        # Download do áudio
        start_time = time.time()
        audio_file, download_time = download_audio_from_youtube(youtube_url)
        
        if not audio_file:
            logging.error("Falha ao baixar o áudio do YouTube. Saindo.")
            exit(1)
        
        logging.info(f"Áudio do YouTube baixado e salvo em {audio_file} em {download_time:.2f} segundos")

    # Processamento comum para todas as opções
    # Reduzir taxa de amostragem
    audio_file_reduced, conversion_time = reduce_sample_rate(audio_file, WAVE_OUTPUT_FILENAME_REDUCED, 8000)

    if not audio_file_reduced:
        logging.error("Falha ao reduzir a taxa de amostragem. Saindo.")
        exit(1)
    
    logging.info(f"Áudio com taxa de amostragem reduzida e salvo em {audio_file_reduced} em {conversion_time:.2f} segundos")

    # Converter para MP3
    output_dir = os.path.dirname(MP3_OUTPUT_FILENAME)
    os.makedirs(output_dir, exist_ok=True)

    audio_file_mp3, conversion_time = convert_to_mp3(audio_file_reduced, MP3_OUTPUT_FILENAME)
    
    if not audio_file_mp3:
        logging.error("Falha ao converter para MP3. Saindo.")
        exit(1)
    
    logging.info(f"Áudio convertido para MP3 e salvo em {audio_file_mp3} em {conversion_time:.2f} segundos")

    # Transcrever o áudio
    logging.info("\nTranscrevendo o áudio com a API Gemini...")
    start_time = time.time()
    transcricao_original, transcription_time = transcribe_audio_gemini(audio_file_mp3)

    if transcricao_original:
        # Corrigir a transcrição com o Gemini
        logging.info("Corrigindo a transcrição com o Gemini...\n")
        transcricao_corrigida = correct_transcript_gemini(transcricao_original)

        if transcricao_corrigida:
            logging.info(f"Transcrição corrigida (Gemini):\n{transcricao_corrigida}\n")
            logging.info(f"\nTempo de transcrição: {transcription_time:.2f} segundos")
        else:
            logging.error("Falha ao corrigir a transcrição com o Gemini.")
    else:
        logging.error("Falha ao transcrever o áudio com a API Gemini.")
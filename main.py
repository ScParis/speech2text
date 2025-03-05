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
import threading
import mimetypes
import queue

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
RETRY_COUNT = 3

OUTPUT_DIR = "output_files"  # Define your output directory

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

WAVE_OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, "output.wav")
MP3_OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, "output.mp3")
WAVE_OUTPUT_FILENAME_REDUCED = os.path.join(OUTPUT_DIR, "output_reduced.wav")
YOUTUBE_AUDIO_FILENAME = os.path.join(OUTPUT_DIR, "youtube_audio.webm")
VIDEO_AUDIO_FILENAME = os.path.join(OUTPUT_DIR, "video_audio.wav")
TIKTOK_VIDEO_FILENAME = os.path.join(OUTPUT_DIR, "tiktok_video.mp4")
INSTAGRAM_VIDEO_FILENAME = os.path.join(OUTPUT_DIR, "instagram_video.mp4")

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

def get_user_input(prompt, validation_func=None, error_message=None, timeout=None):
    """Função para solicitar entrada do usuário com validação e timeout."""
    result_queue = queue.Queue()

    def input_with_timeout(prompt, result_queue):
        try:
            user_input = input(prompt)
            result_queue.put(user_input)
        except Exception as e:
            logging.error(f"Erro ao obter entrada do usuário: {e}")
            result_queue.put(None)  # Sinaliza um erro

    input_thread = threading.Thread(target=input_with_timeout, args=(prompt, result_queue))
    input_thread.daemon = True  # Permite que o programa saia mesmo se este thread estiver bloqueado
    input_thread.start()

    try:
        user_input = result_queue.get(timeout=timeout)
    except queue.Empty:
        print("\nTempo limite excedido. Nenhuma entrada detectada.")
        return None  # Retorna None se o tempo limite for atingido

    if user_input is None:
        return None  # Retorna None se houver um erro na entrada

    if not validation_func or validation_func(user_input):
        return user_input.strip()
    else:
        print(error_message or "Entrada inválida. Por favor, tente novamente.")
        return None  # Retorna None para entrada inválida

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

def download_audio_from_youtube(youtube_url):
    """Baixa o áudio de um vídeo do YouTube e salva em um arquivo WEBM."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': YOUTUBE_AUDIO_FILENAME,  # Salva na pasta output_files
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
        return YOUTUBE_AUDIO_FILENAME, download_time  # Retorna o caminho completo
    except Exception as e:
        logging.error(f"Erro ao baixar o áudio do YouTube: {e}")
        return None, None

def download_with_credentials(url, username, password):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': YOUTUBE_AUDIO_FILENAME,  # Salva na pasta output_files
        'extractaudio': True,
        'audioformat': 'webm',
        'noplaylist': True,
        'logger': MyLogger(),
        'progress_hooks': [],
        'quiet': True,
        'force': True,
        'no_warnings': True,
        'username': username,
        'password': password,
    }
    start_time_download = time.time()
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        download_time = time.time() - start_time_download
        logging.info(f"Download de áudio do YouTube com credenciais concluído em {download_time:.2f} segundos")
        return YOUTUBE_AUDIO_FILENAME, download_time
    except Exception as e:
        logging.error(f"Erro ao baixar o áudio do YouTube com credenciais: {e}")
        return None, None

def download_tiktok_video(tiktok_url):
    """Baixa o vídeo de um link do TikTok."""
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': TIKTOK_VIDEO_FILENAME,  # Caminho para salvar o vídeo
            'noplaylist': True,
            'nocheckcertificate': True,  # Ignorar erros de certificado
            'quiet': True,  # Modo silencioso
            'no_warnings': True,
            'logger': MyLogger(),
            'progress_hooks': [],
            'force': True,
        }
        start_time_download = time.time()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tiktok_url])
        download_time = time.time() - start_time_download
        logging.info(f"Vídeo do TikTok baixado com sucesso em {download_time:.2f} segundos")
        return TIKTOK_VIDEO_FILENAME, download_time
    except Exception as e:
        logging.error(f"Erro ao baixar o vídeo do TikTok: {e}")
        return None, None

def download_instagram_story(instagram_url, username=None, password=None):
    """Baixa o vídeo de um link do Instagram Stories."""
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': INSTAGRAM_VIDEO_FILENAME,  # Caminho para salvar o vídeo
            'noplaylist': True,
            'nocheckcertificate': True,  # Ignorar erros de certificado
            'quiet': True,  # Modo silencioso
            'no_warnings': True,
            'logger': MyLogger(),
            'progress_hooks': [],
            'force': True,
            'http_header': {  # Adicionar cabeçalhos HTTP
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        }

        # Adicionar credenciais se fornecidas
        if username and password:
            ydl_opts['username'] = username
            ydl_opts['password'] = password

        start_time_download = time.time()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([instagram_url])
        download_time = time.time() - start_time_download
        logging.info(f"Vídeo do Instagram baixado com sucesso em {download_time:.2f} segundos")
        return INSTAGRAM_VIDEO_FILENAME, download_time
    except Exception as e:
        logging.error(f"Erro ao baixar o vídeo do Instagram: {e}")
        if "You need to log in to access this content" in str(e):
            logging.error("O vídeo do Instagram é privado e requer login. Por favor, forneça suas credenciais.")
            print("O vídeo do Instagram é privado e requer login. Por favor, forneça suas credenciais.")
        return None, None

def extract_audio_from_video(video_file, output_file):
    """Extrai o áudio de um arquivo de vídeo usando ffmpeg."""
    try:
        start_time_extraction = time.time()
        subprocess.run([
            "ffmpeg",
            "-i", video_file,
            "-vn",  # Sem vídeo
            "-acodec", "pcm_s16le",  # Codec WAV
            "-ar", "8000",  # Taxa de amostragem
            "-ac", "1",  # Mono
            output_file
        ], check=True, capture_output=True, text=True, timeout=600)  # Limite de tempo de 10 minutos
        extraction_time = time.time() - start_time_extraction
        logging.info(f"Áudio extraído do vídeo e salvo em {output_file} em {extraction_time:.2f} segundos")
        return output_file, extraction_time
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao extrair o áudio do vídeo: {e.stderr}")
        return None, None
    except subprocess.TimeoutExpired:
        logging.error("Tempo limite excedido ao extrair o áudio do vídeo.")
        return None, None
    except FileNotFoundError:
        logging.error("Erro: ffmpeg não encontrado. Certifique-se de que o ffmpeg está instalado e acessível através da linha de comando.")
        return None, None

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
    prompt = f"""Traduza para Português e corrija a ortografia e gramática do texto a seguir, e garanta que o texto está completo e de acordo com o audio original.{transcript}
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
        global MP3_OUTPUT_FILENAME
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

def validate_video_file(file_path):
    """Valida se o arquivo é um arquivo de vídeo com extensões comuns."""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']  # Adicione mais se necessário
    return (
        os.path.isfile(file_path) and
        any(file_path.lower().endswith(ext) for ext in video_extensions)
    )

def is_valid_url(url):
    """Valida se a string é uma URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_audio_file(file_path):
    """Valida se o arquivo é de áudio, verificando a extensão e o tipo MIME."""
    audio_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.webm']
    mime_type, _ = mimetypes.guess_type(file_path)
    return (
        os.path.isfile(file_path) and
        any(file_path.lower().endswith(ext) for ext in audio_extensions) and
        mime_type and mime_type.startswith('audio/')
    )

def is_valid_instagram_story_url(url):
    """Valida se a URL é de um Story do Instagram."""
    instagram_story_regex = r'https?://(?:www\.)?instagram\.com/stories/[a-zA-Z0-9_.]+/([0-9]+)/'
    match = re.match(instagram_story_regex, url)
    return bool(match)

def is_valid_instagram_reel_url(url):
    """Valida se a URL é de um Reel do Instagram."""
    instagram_reel_regex = r'https?://(?:www\.)?instagram\.com/reels/([a-zA-Z0-9_-]+)/?'
    match = re.match(instagram_reel_regex, url)
    return bool(match)

def identify_platform(url):
    """Identifica a plataforma da URL."""
    if is_valid_youtube_url(url):
        return "YouTube"
    elif is_valid_tiktok_url(url):
        return "TikTok"
    elif is_valid_instagram_story_url(url):
        return "Instagram Story"
    elif is_valid_instagram_reel_url(url):
        return "Instagram Reel"
    elif is_valid_url(url):
        return "Generic"
    else:
        return None

def process_transcription(audio_file):
    """Processa a transcrição do áudio, incluindo redução da taxa de amostragem, conversão para MP3 e transcrição com a API Gemini."""
    try:
        # Reduzir taxa de amostragem
        audio_file_reduced, conversion_time = reduce_sample_rate(audio_file, WAVE_OUTPUT_FILENAME_REDUCED, 8000)
        if not audio_file_reduced:
            logging.error("Falha ao reduzir a taxa de amostragem.")
            return None
        logging.info(f"Áudio com taxa de amostragem reduzida e salvo em {audio_file_reduced} em {conversion_time:.2f} segundos")

        # Converter para MP3
        output_dir = os.path.dirname(MP3_OUTPUT_FILENAME)
        os.makedirs(output_dir, exist_ok=True)

        audio_file_mp3, conversion_time = convert_to_mp3(audio_file_reduced, MP3_OUTPUT_FILENAME)
        if not audio_file_mp3:
            logging.error("Falha ao converter para MP3.")
            return None
        logging.info(f"Áudio convertido para MP3 e salvo em {audio_file_mp3} em {conversion_time:.2f} segundos")

        # Transcrever o áudio
        logging.info("\nTranscrevendo o áudio com a API Gemini...")
        transcricao_original, transcription_time = transcribe_audio_gemini(audio_file_mp3)
        return transcricao_original
    except Exception as e:
        logging.error(f"Erro durante o processo de transcrição: {e}")
        return None

def improve_transcript(transcricao_original):
    """Melhora a transcrição original com o Gemini."""
    prompt = f"Traduza para Português e corrija a gramática, a ortografia e o estilo do seguinte texto. Faça uma análise profunda e apresente um resumo e percepções sobre o Texto:\n{transcricao_original}"
    texto_gerado = generate_text_gemini(prompt)
    return texto_gerado

# Variável para controlar o loop principal
continue_processing = True
start_time = None  # Inicializa start_time aqui

def main():
    """Função principal para iniciar o processo."""
    global continue_processing
    global start_time  # Declara start_time como global

    # Limpar diretório de saída
    clear_output_directory()
    start_time = time.time()  # Inicializa start_time aqui

    # Loop principal
    while continue_processing:
        # Menu de opções
        logging.info("Escolha uma opção de entrada:")
        logging.info("1. Gravação de voz")
        logging.info("2. Envio de arquivo (áudio ou vídeo)")
        logging.info("3. Envio de link")

        # Solicitar opção com validação e timeout
        opcao = get_user_input(
            "Digite 1, 2 ou 3: ",
            validation_func=lambda x: x in ['1', '2', '3'],
            error_message="Por favor, digite 1, 2 ou 3.",
            timeout=15  # Timeout para a escolha da opção
        )

        if opcao is None:
            continue_processing = False  # Encerra a execução se o tempo limite for atingido
            break

        audio_file = None  # Inicializa audio_file aqui

        if opcao == "1":
            # Gravação de voz
            logging.info("Preparando para gravar. Certifique-se de que o microfone está conectado.")
            audio_file = record_audio()
            if not audio_file:
                logging.error("Falha na gravação de áudio. Saindo.")
                continue
            record_time = time.time() - start_time
            logging.info(f"Áudio gravado e salvo em {audio_file} em {record_time:.2f} segundos")

        elif opcao == "2":
            # Envio de arquivo (áudio ou vídeo)
            file_path = get_user_input(
                "Digite o caminho completo para o arquivo (áudio ou vídeo): ",
                validation_func=lambda x: validate_audio_file(x) or validate_video_file(x),
                error_message="Arquivo inválido ou não encontrado. Verifique o caminho e a extensão.",
                timeout=15  # Adicionado timeout de 15 segundos
        )
            if not file_path:
                print("Entrada inválida ou tempo limite excedido.")
                continue
 
            logging.info(f"Arquivo especificado: {file_path}")
            if validate_video_file(file_path):
                audio_file, extraction_time = extract_audio_from_video(file_path, VIDEO_AUDIO_FILENAME)
                if not audio_file:
                    logging.error("Falha ao extrair o áudio do vídeo. Saindo.")
                    continue
                logging.info(f"Áudio extraído do vídeo e salvo em {audio_file} em {extraction_time:.2f} segundos")
            elif validate_audio_file(file_path):
                audio_file = file_path
            else:
                logging.error("Formato de arquivo não suportado.")
                print("Formato de arquivo não suportado.")
                continue

        elif opcao == "3":
            # Envio de link
            url = get_user_input(
                "Digite a URL da plataforma: ",
                validation_func=is_valid_url,
                error_message="URL inválida. Verifique o link.",
                timeout=15  # Adicionado timeout de 15 segundos
        )
            if not url:
                print("Entrada inválida ou tempo limite excedido.")
                continue
 
            platform = identify_platform(url)
            logging.info(f"Identificada plataforma: {platform}")

            # Solicitar credenciais se a plataforma for Instagram
            username, password = None, None
            if platform == "Instagram Story" or platform == "Instagram Reel":
                username = get_user_input("Digite o nome de usuário do Instagram (se necessário, deixe em branco para público): ", validation_func=lambda x: True)
                password = get_user_input("Digite a senha do Instagram (se necessário, deixe em branco para público): ", validation_func=lambda x: True)

            try:
                # Tratamento para YouTube
                if platform == "YouTube":
                    if username and password:
                        audio_file, download_time = download_with_credentials(url, username, password)
                    else:
                        audio_file, download_time = download_audio_from_youtube(url)
    
                    if not audio_file:
                        logging.error("Falha ao baixar o áudio do YouTube. Saindo.")
                        print("Ocorreu um erro ao baixar o áudio do YouTube. Verifique a URL e tente novamente.")
                        continue
                    logging.info(f"Áudio do YouTube baixado e salvo em {audio_file} em {download_time:.2f} segundos")
    
                # Tratamento para TikTok
                elif platform == "TikTok":
                    audio_file, download_time = download_tiktok_video(url)
                    if not audio_file:
                        logging.error("Falha ao baixar o vídeo do TikTok. Saindo.")
                        print("Ocorreu um erro ao baixar o vídeo do TikTok. Verifique a URL e tente novamente.")
                        continue
  
                    audio_file, extraction_time = extract_audio_from_video(audio_file, VIDEO_AUDIO_FILENAME)
                    if not audio_file:
                        logging.error("Falha ao extrair áudio do vídeo do TikTok. Saindo.")
                        print("Ocorreu um erro ao extrair o áudio do vídeo do TikTok. Verifique se o FFmpeg está instalado corretamente.")
                        continue
                    logging.info(f"Áudio extraído do vídeo do TikTok e salvo em {audio_file} em {extraction_time:.2f} segundos")

                 # Tratamento para Instagram
                elif platform == "Instagram Story" or platform == "Instagram Reel":
                    if username and password:
                        audio_file, download_time = download_instagram_story(url, username, password)
                    else:
                        logging.error("Impossivel obter o audio do Instagram sem usuário e senha.")
                        print("Para acessar este conteúdo, pode ser necessário logar na conta do Instagram ou o perfil é privado.")
                        continue  # Pula para a próxima iteração sem erro
                    
                    if not audio_file:
                        logging.error("Falha ao baixar o vídeo do Instagram. Saindo.")
                        print("Para acessar este conteúdo, pode ser necessário logar na conta do Instagram ou o perfil é privado.")
                        continue_processing = False  # Encerra a execução
                        break

                    # Verifique se audio_file está definido antes de extrair o áudio
                    audio_file, extraction_time = extract_audio_from_video(audio_file, VIDEO_AUDIO_FILENAME)
                    if not audio_file:
                        logging.error(f"Falha ao extrair áudio do vídeo do Instagram. Saindo: {e}")
                        print("Ocorreu um erro ao extrair o áudio do vídeo do Instagram. Verifique as credenciais e tente novamente.")
                        continue_processing = False  # Encerra a execução
                        break
                    logging.info(f"Áudio extraído do vídeo do Instagram e salvo em {VIDEO_AUDIO_FILENAME} em {extraction_time:.2f} segundos")
                    

# Restante do código
                # Outras plataformas
                else:
                    print("Plataforma não suportada. A transcrição de áudio para esta plataforma não é suportada.")
                    continue

            except Exception as e:
                logging.error(f"Ocorreu um erro ao processar o link: {e}")
                print(f"Ocorreu um erro ao processar o link: {e}")
                continue

        else:
            logging.error("Opção inválida.")
            print("Opção inválida.")
            continue

        if not audio_file:
            print("Falha ao obter o arquivo de áudio. Encerrando.")
            continue_processing = False  # Encerra a execução
            break

        # Processar a transcrição
        try:
            transcricao_original = process_transcription(audio_file)
            if not transcricao_original:
                print("Falha ao obter a transcrição original.")
            else:

                logging.info("Aprimorando a transcrição com o Gemini...\n")
                print(f"\nTranscrição original (Gemini):\n{transcricao_original}\n")

                texto_gerado = improve_transcript(transcricao_original)

                if texto_gerado:
                    print(f"\nTranscrição aprimorada (Gemini):\n{texto_gerado}")
                else:
                    print("Falha ao aprimorar a transcrição com o Gemini.")

        except Exception as e:
            logging.error(f"Ocorreu um erro durante o processamento: {e}")

        # Finalizar o processo e aguardar a resposta do usuário por 10 segundos
        def finalizar_apos_timeout():
            global continue_processing
            print("\nNenhuma interação detectada. Finalizando a execução.")
            continue_processing = False

        timer = threading.Timer(10.0, finalizar_apos_timeout)
        timer.start()

        user_choice = get_user_input(
            "\nDeseja realizar novo envio (s/n)? ",
            validation_func=lambda x: x.lower() in ['s', 'n'],
            error_message="Por favor, digite 's' para sim ou 'n ' para não.",
            timeout=10  # Timeout para a escolha do usuário
        )

        timer.cancel()  # Cancela o timer
        
        if user_choice is None or user_choice.lower() == 'n':
            print("Finalizando a execução.")
            continue_processing = False

    logging.info("Execução finalizada.")

# Funções auxiliares
def clear_output_directory():
    """
    Remove todos os arquivos do diretório de saída.
    """
    try:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)  # Remove o diretório e seu conteúdo
        os.makedirs(OUTPUT_DIR)          # Recria o diretório
        logging.info(f"Diretório de saída limpo: {OUTPUT_DIR}")
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
        
        # YouTube Music
        r'(https?://)?(music\.youtube\.com)/(watch\?v=|embed/|v/)?([^&=%\?]{11})',
        
        # Links com parâmetros adicionais
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/)?([^&=%\?]{11})(\?.*)?'
    ]
    
    for pattern in youtube_regex_patterns:
        match = re.match(pattern, url)
        if match:
            return True
    return False

def is_valid_tiktok_url(url):
    """Valida se a URL é de um vídeo do TikTok."""
    tiktok_regex = r'https?://(?:m|www|vm)\.tiktok\.com/(?:.+/)?(?:video/)?([0-9]+)'
    match = re.match(tiktok_regex, url)
    return bool(match)

def is_valid_instagram_story_url(url):
    """Valida se a URL é de um Story do Instagram."""
    instagram_story_regex = r'https?://(?:www\.)?instagram\.com/stories/[a-zA-Z0-9_.]+/([0-9]+)/'
    match = re.match(instagram_story_regex, url)
    return bool(match)

def is_valid_instagram_reel_url(url):
    """Valida se a URL é de um Reel do Instagram."""
    instagram_reel_regex = r'https?://(?:www\.)?instagram\.com/reels/([a-zA-Z0-9_-]+)/?'
    match = re.match(instagram_reel_regex, url)
    return bool(match)

def is_valid_url(url):
    """Valida se a string é uma URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_audio_file(file_path):
    """Valida se o arquivo é de áudio, verificando a extensão e o tipo MIME."""
    audio_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.webm']
    mime_type, _ = mimetypes.guess_type(file_path)
    return (
        os.path.isfile(file_path) and
        any(file_path.lower().endswith(ext) for ext in audio_extensions) and
        mime_type and mime_type.startswith('audio/')
    )

def validate_video_file(file_path):
    """Valida se o arquivo é um arquivo de vídeo com extensões comuns."""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']  # Adicione mais se necessário
    return (
        os.path.isfile(file_path) and
        any(file_path.lower().endswith(ext) for ext in video_extensions)
    )

def identify_platform(url):
    """Identifica a plataforma da URL."""
    if is_valid_youtube_url(url):
        return "YouTube"
    elif is_valid_tiktok_url(url):
        return "TikTok"
    elif is_valid_instagram_story_url(url):
        return "Instagram Story"
    elif is_valid_instagram_reel_url(url):
        return "Instagram Reel"
    elif is_valid_url(url):
        return "Generic"
    else:
        return None

if __name__ == '__main__':
    # Only run the CLI interface if this file is run directly
    main()
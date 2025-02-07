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
import math #para calculo de divisões

# Configurações de gravação
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000 #ALTERADO - REDUZIR A TAXA DE AMOSTRAGEM
RECORD_SECONDS = 1  # Grava por 5 segundos
WAVE_OUTPUT_FILENAME = "output.wav"
MP3_OUTPUT_FILENAME = "output.mp3" # Adicionado arquivo de saída MP3
WAVE_OUTPUT_FILENAME_REDUCED = "output_reduced.wav" # Defina a variável aqui

# Configurações da API Gemini (Carregadas do config.py)
# API_KEY = "SUA_CHAVE_DE_API_DO_GEMINI"  # Remova esta linha
GEMINI_API_URL = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}" # Usar a variável GEMINI_API_URL do config.py

class MyLogger(object):
    def __init__(self):
        self.pbar = None

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

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
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Gravando...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Fim da gravação.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def download_audio_from_youtube(youtube_url, output_filename="youtube_audio.webm"):
    """Baixa o áudio de um vídeo do YouTube e salva em um arquivo WEBM."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_filename,
            'extractaudio': True,
            'audioformat': 'webm',  # Converter para WEBM
            'noplaylist': True,
            'logger': MyLogger(),
            'progress_hooks': [],
            'quiet': True, # Remover mensagens de progresso
        }
        start_time_download = time.time()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_filename, time.time() - start_time_download
    except Exception as e:
        print(f"Erro ao baixar o áudio do YouTube: {e}")
        return None, None

def reduce_sample_rate(input_file, output_file, new_rate):
    """Reduz a taxa de amostragem de um arquivo de áudio usando ffmpeg."""
    try:
        start_time_conversion = time.time()
        subprocess.run([
            "ffmpeg",
            "-i", input_file,
            "-ar", str(new_rate),
            output_file
        ], check=True, capture_output=True, text=True, timeout=600) # Limite de tempo de 10 minutos
        return output_file, time.time() - start_time_conversion
    except subprocess.CalledProcessError as e:
        print(f"Erro ao reduzir a taxa de amostragem: {e.stderr}")
        return None, None
    except subprocess.TimeoutExpired:
        print("Tempo limite excedido ao reduzir a taxa de amostragem.")
        return None, None
    except FileNotFoundError:
        print("Erro: ffmpeg não encontrado. Certifique-se de que o ffmpeg está instalado e acessível através da linha de comando.")
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
        print(f"Erro ao converter para MP3: {e.stderr}")
        return None, None
    except subprocess.TimeoutExpired:
        print("Tempo limite excedido ao converter para MP3.")
        return None, None
    except FileNotFoundError:
        print("Erro: ffmpeg não encontrado. Certifique-se de que o ffmpeg está instalado e acessível através da linha de comando.")
        return None, None

def transcribe_audio_gemini(audio_file):
    """Transcreve um arquivo de áudio usando a API Gemini e implementa a diarização."""
    try:
        with open(audio_file, "rb") as f:
            audio_data = f.read()

        # Codifica o áudio em Base64
        audio_encoded = base64.b64encode(audio_data).decode("utf-8")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": """
                            Transcreva o áudio a seguir para texto, identificando os personagens que estão falando e indicando quem fala o quê.
                            Se possível, identifique os nomes dos personagens. Se não for possível, use "Personagem 1" e "Personagem 2".
                            Formate a transcrição da seguinte forma:
                            [Nome do Personagem 1]: [Fala do personagem 1]
                            [Nome do Personagem 2]: [Fala do personagem 2]
                            ...
                            Se houver sobreposição de falas, indique isso claramente.
                            Tente inferir o contexto da conversa e usar essa informação para melhorar a precisão da transcrição e a identificação dos personagens.
                            Se a Simone falar "Oi", responda com "[Simone]: Oi"
                            Se o Diego responder, responda com "[Diego]:"
                            """
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

        #print("Payload JSON:", json.dumps(payload))  # Removido para reduzir a saída
        start_time_transcription = time.time()
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload), timeout=600)
        transcription_time = time.time() - start_time_transcription
        #print("Resposta da API Gemini:", response.text) # Removido para reduzir a saída

        response.raise_for_status()

        result = response.json()

        # Extrai o texto gerado da resposta
        try:
            transcript = result["candidates"][0]["content"]["parts"][0]["text"]
            # Estruturar a transcrição
            structured_transcript = format_transcript(transcript)
            return structured_transcript, transcription_time
        except (KeyError, IndexError):
            print("Erro ao extrair a transcrição da resposta do Gemini.")
            print("Resposta completa do Gemini:", result)
            return None, None

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {audio_file}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para a API Gemini: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar a resposta JSON da API Gemini: {e}")
        return None, None
    except Exception as e:
        print(f"Erro geral na transcrição com Gemini: {e}")
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
            print("Erro ao extrair o texto da resposta da API Gemini.")
            print("Resposta completa do Gemini:", result)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição à API Gemini: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar a resposta JSON da API Gemini: {e}")
        return None

def format_transcript(transcript):
    """Formata a transcrição para identificar os personagens e suas falas."""
    lines = transcript.splitlines()
    structured_transcript = ""
    personagem_atual = "Personagem 1" # Valor inicial
    personagens = {} # Dicionário para mapear personagens a falas

    padrao_personagem = re.compile(r"\[(.*?)\]:\s*(.*)")
    for line in lines:
        # Tentar identificar o personagem (se a linha começar com "[Nome do Personagem]:")
        match = padrao_personagem.match(line)
        if match:
            personagem = match.group(1)
            fala = match.group(2)
            #Remover "Personagem"
            personagem = personagem.replace("Personagem ", "")
            structured_transcript += f"{personagem}: {fala}\n"
        else:
            # Se não conseguir identificar o personagem, apenas imprimir a linha
            structured_transcript += f"{personagem_atual}: {line}\n"
    return structured_transcript

def correct_transcript_gemini(transcript):
    """Corrigir a transcrição com o Gemini."""
    prompt = f"""Corrija a ortografia e gramática do texto a seguir e substitua "Papurã" por "PipeRun", se a transcrição estiver relacionada a empresa:
    {transcript}
    """
    corrected_transcript = generate_text_gemini(prompt)

    if corrected_transcript:
        return corrected_transcript
    else:
        print("Falha ao corrigir a transcrição com o Gemini.")
        return transcript

if __name__ == "__main__":

    # 0. Escolher a fonte do áudio
    print("Escolha uma opção:")
    print("1. Gravar áudio do microfone")
    print("2. Fornecer o caminho para um arquivo de áudio existente")
    print("3. Fornecer um link do YouTube")
    opcao = input("Digite 1, 2 ou 3: ")

    if opcao == "1":
        # 1. Gravar o áudio
        print("Preparando para gravar. Certifique-se de que o microfone está conectado e configurado.")
        start_time = time.time()
        record_audio()
        record_time = time.time() - start_time
        print(f"Áudio gravado e salvo em {WAVE_OUTPUT_FILENAME} em {record_time:.2f} segundos")
        audio_file = WAVE_OUTPUT_FILENAME
    elif opcao == "2":
        # 1. Fornecer o caminho para um arquivo de áudio
        audio_file = input("Digite o caminho completo para o arquivo de áudio: ")
        if not audio_file:
            print("Nenhum arquivo especificado. Saindo.")
            exit()
        print(f"Arquivo de áudio especificado: {audio_file}")
    elif opcao == "3":
        # 1. Fornecer um link do YouTube
        youtube_url = input("Digite o link do YouTube: ")
        # Validar a URL
        regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([a-zA-Z0-9_-]{11})$"
        if not re.match(regex, youtube_url):
            print("URL do YouTube inválida. Saindo.")
            exit()

        start_time = time.time()
        audio_file, download_time = download_audio_from_youtube(youtube_url, output_filename="youtube_audio.webm") # Baixar o vídeo completo
        if not audio_file:
            print("Falha ao baixar o áudio do YouTube. Saindo.")
            exit()
        download_time = time.time() - start_time
        print(f"Áudio do YouTube baixado e salvo em {audio_file} em {download_time:.2f} segundos")
    else:
        print("Opção inválida. Saindo.")
        exit()

    #Reduzir taxa de amostragem
    audio_file_reduced, conversion_time = reduce_sample_rate(audio_file, WAVE_OUTPUT_FILENAME_REDUCED, 8000)

    if not audio_file_reduced:
        print("Falha ao reduzir a taxa de amostragem. Saindo.")
        exit()
    print(f"Áudio com taxa de amostragem reduzida e salvo em {audio_file_reduced} em {conversion_time:.2f} segundos")

    # Converter para MP3
    audio_file_mp3, conversion_time = convert_to_mp3(audio_file_reduced, MP3_OUTPUT_FILENAME)
    if not audio_file_mp3:
        print("Falha ao converter para MP3. Saindo.")
        exit()
    print(f"Áudio convertido para MP3 e salvo em {audio_file_mp3} em {conversion_time:.2f} segundos")

    # 2. Transcrever o áudio (usando a API Gemini)
    print("Transcrevendo o áudio com a API Gemini...")
    start_time = time.time()
    transcricao_original, transcription_time = transcribe_audio_gemini(audio_file_mp3)

    if transcricao_original:
        print(f"Transcrição original (Gemini):\n{transcricao_original}\n")
        print(f"Tempo de transcrição: {transcription_time:.2f} segundos")

        # Corrigir a transcrição com o Gemini
        print("Corrigindo a transcrição com o Gemini...")
        transcricao_corrigida = correct_transcript_gemini(transcricao_original)

        if transcricao_corrigida:
            print(f"Transcrição corrigida (Gemini):\n{transcricao_corrigida}\n")
        else:
            print("Falha ao corrigir a transcrição com o Gemini.")

        # 3. Aprimorar a transcrição com o Gemini (opcional)
        # prompt = f"Corrija a gramática, a ortografia e o estilo do seguinte texto:\n{transcricao_original}"
        # texto_gerado = generate_text_gemini(prompt)

        # if texto_gerado:
        #     print(f"Transcrição aprimorada (Gemini):\n{texto_gerado}")
        # else:
        #     print("Falha ao aprimorar a transcrição com o Gemini.")
        print("Aprimoramento com Gemini desativado por enquanto.")
    else:
        print("Falha ao transcrever o áudio com a API Gemini.")
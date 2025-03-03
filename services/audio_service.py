import os
import sys
import pyaudio
import wave
import yt_dlp
import subprocess
import logging

# Ajuste do path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import AUDIO_CONFIG, OUTPUT_DIR

class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): logging.error(msg)

def record_audio():
    """Grava áudio do microfone"""
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=getattr(pyaudio, AUDIO_CONFIG["FORMAT"]),
                       channels=AUDIO_CONFIG["CHANNELS"],
                       rate=AUDIO_CONFIG["RATE"],
                       input=True,
                       frames_per_buffer=AUDIO_CONFIG["CHUNK"])

        frames = []
        for _ in range(0, int(AUDIO_CONFIG["RATE"] / AUDIO_CONFIG["CHUNK"] * AUDIO_CONFIG["RECORD_SECONDS"])):
            data = stream.read(AUDIO_CONFIG["CHUNK"])
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        output_file = os.path.join(OUTPUT_DIR, "recorded_audio.wav")
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(AUDIO_CONFIG["CHANNELS"])
            wf.setsampwidth(p.get_sample_size(getattr(pyaudio, AUDIO_CONFIG["FORMAT"])))
            wf.setframerate(AUDIO_CONFIG["RATE"])
            wf.writeframes(b''.join(frames))
        
        return output_file
    except Exception as e:
        logging.error(f"Erro na gravação de áudio: {e}")
        return None

def download_audio_from_youtube(url):
    """Download de áudio do YouTube"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_base = os.path.join(OUTPUT_DIR, "youtube_audio")
        output_temp = f"{output_base}.webm"
        output_final = f"{output_base}.wav"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_temp,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # O arquivo final terá extensão .wav após o pós-processamento
        if os.path.exists(output_final):
            return output_final, None
        else:
            logging.error(f"Arquivo de saída não encontrado: {output_final}")
            return None, "Arquivo de saída não encontrado"
            
    except Exception as e:
        logging.error(f"Erro no download do YouTube: {e}")
        return None, str(e)

def extract_audio_from_video(video_file, output_file):
    """Extrai áudio de um arquivo de vídeo"""
    try:
        subprocess.run([
            'ffmpeg', '-i', video_file,
            '-vn', '-acodec', 'pcm_s16le',
            '-ar', str(AUDIO_CONFIG["RATE"]),
            '-ac', str(AUDIO_CONFIG["CHANNELS"]),
            output_file
        ], check=True, capture_output=True)
        return output_file, None
    except Exception as e:
        logging.error(f"Erro na extração de áudio: {e}")
        return None, str(e)

def download_tiktok_video(url):
    """Download de vídeo do TikTok"""
    try:
        output_file = os.path.join(OUTPUT_DIR, "tiktok_video.mp4")
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_file,
            'logger': MyLogger(),
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return output_file, None
    except Exception as e:
        logging.error(f"Erro no download do TikTok: {e}")
        return None, str(e)

def download_instagram_story(url):
    """Download de story do Instagram"""
    try:
        output_file = os.path.join(OUTPUT_DIR, "instagram_video.mp4")
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_file,
            'logger': MyLogger(),
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return output_file, None
    except Exception as e:
        logging.error(f"Erro no download do Instagram: {e}")
        return None, str(e)

import os
import pyaudio
import wave
import yt_dlp
import subprocess
import shutil
import logging

# Configurações globais
OUTPUT_DIR = "output_files"

# Configure o logging de forma centralizada se necessário
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def record_audio(duration=5, rate=16000, channels=1, chunk=1024, 
                 output_filename=os.path.join(OUTPUT_DIR, "recorded_audio.wav")):
    """Grava áudio por um período especificado e salva em um arquivo WAV."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []
    for _ in range(0, int(rate / chunk * duration)):
        frames.append(stream.read(chunk))
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return output_filename


def download_audio_from_youtube(url, output_file=os.path.join(OUTPUT_DIR, "youtube_audio.mp3")):
    """Baixa áudio do YouTube e converte para MP3 usando yt-dlp e FFmpeg."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_file.replace('.mp3', ''),
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_file


def extract_audio_from_video(video_path, output_audio_path):
    """Extrai o áudio de um vídeo usando FFmpeg."""
    command = f"ffmpeg -i \"{video_path}\" -q:a 0 -map a \"{output_audio_path}\" -y"
    subprocess.run(command, shell=True, check=True)
    return output_audio_path


def convert_to_mp3(file_path, output_file=os.path.join(OUTPUT_DIR, "output.mp3")):
    """Converte um arquivo de áudio para MP3 usando FFmpeg."""
    command = f"ffmpeg -i \"{file_path}\" -codec:a libmp3lame -qscale:a 2 \"{output_file}\" -y"
    subprocess.run(command, shell=True, check=True)
    return output_file

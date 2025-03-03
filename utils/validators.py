import re
from urllib.parse import urlparse
import mimetypes
import os

def validate_audio_file(file_path):
    """Valida se o arquivo é de áudio"""
    audio_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.webm']
    mime_type, _ = mimetypes.guess_type(file_path)
    return (
        os.path.isfile(file_path) and
        any(file_path.lower().endswith(ext) for ext in audio_extensions) and
        mime_type and mime_type.startswith('audio/')
    )

def validate_video_file(file_path):
    """Valida se o arquivo é um vídeo"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    return (
        os.path.isfile(file_path) and
        any(file_path.lower().endswith(ext) for ext in video_extensions)
    )

def is_valid_youtube_url(url):
    """
    Valida se a URL é do YouTube, incluindo:
    - URLs padrão
    - URLs curtas (youtu.be)
    - Shorts
    - URLs com parâmetros
    """
    youtube_patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/v/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)

def is_valid_tiktok_url(url):
    """Valida se a URL é do TikTok"""
    tiktok_pattern = r'https?://(?:www\.)?tiktok\.com/.*'
    return bool(re.match(tiktok_pattern, url))

def is_valid_instagram_url(url):
    """Valida se a URL é do Instagram"""
    instagram_patterns = [
        r'https?://(?:www\.)?instagram\.com/stories/[^/]+/\d+',
        r'https?://(?:www\.)?instagram\.com/reel/[\w-]+',
        r'https?://(?:www\.)?instagram\.com/p/[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in instagram_patterns)

def identify_platform(url):
    """Identifica a plataforma da URL"""
    if is_valid_youtube_url(url):
        return "YouTube"
    elif is_valid_tiktok_url(url):
        return "TikTok"
    elif is_valid_instagram_url(url):
        if '/stories/' in url:
            return "Instagram Story"
        elif '/reel/' in url:
            return "Instagram Reel"
    return None

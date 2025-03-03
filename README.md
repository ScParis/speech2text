# Speech to Text Transcriber

## Descrição
Aplicativo de transcrição de áudio usando a API Gemini.

## Estrutura do Projeto
```
speech2text/
├── config/         # Configurações do projeto
├── services/       # Serviços principais
├── utils/         # Utilitários
├── gui/           # Interface gráfica
├── output_files/  # Arquivos gerados
└── tests/         # Testes
```

## Instalação
```bash
pip install -r requirements.txt
```

## Uso
```bash
python gui_app.py
```

## Requisitos
- Python 3.8+
- PyQt5
- Gemini API key

# Speech-to-Text Transcriber

A multi-platform transcription solution with GUI and CLI interfaces, powered by [@ScParis](https://github.com/ScParis).

Use at your own risk...

## Features

### Core Capabilities
- 🎙️ **Multi-source Input**
  - Microphone recording (WAV format)
  - File upload (MP3, WAV, video formats)
  - URL processing (YouTube, TikTok, Instagram)
- 🤖 **AI-Powered Processing**
  - Gemini API integration for accurate transcription
  - Automatic grammar correction
  - Speaker differentiation
- 📂 **Multi-format Output**
  - Raw transcription
  - Enhanced formatted text
  - Export to TXT files

### GUI Features
- 🎨 Modern dark theme interface
- 🔐 Encrypted credential storage
- 📊 Real-time progress tracking
- ⚡ One-click operations

### CLI Features
- 🖥️ Console-based interface
- 🔄 Batch processing support
- 🌐 Advanced platform support:
  - YouTube (public/private videos)
  - TikTok videos
  - Instagram Stories/Reels (requires credentials)

## Installation

### Prerequisites
- Python 3.9+
- FFmpeg (for audio processing)
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg
```

### Setup
1. Clone repository:
```bash
git clone https://github.com/ScParis/speech2text.git
cd speech2text
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### GUI Configuration
1. Launch application:
```bash
python gui_app.py
```

2. Click settings icon (⚙️) and configure:
   - **API Key**: Gemini authentication key
   - **API URL**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`
   or
   - **API URL**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent`

3. Credentials are encrypted using AES-256

### CLI Configuration
Set environment variables:
```bash
# Linux/Mac
export GEMINI_API_KEY='your_api_key'
export GEMINI_API_URL='https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'

# Windows
setx GEMINI_API_KEY "your_api_key"
setx GEMINI_API_URL "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
```

## Usage

### GUI Application
```bash
python gui_app.py
```

1. **Record Audio**  
   - Click microphone icon
   - Speak for up to 5 seconds
   - Automatic transcription

2. **Process Files**  
   - Supported formats: MP3, WAV, MP4, WEBM
   - Click upload button
   - Select audio/video file

3. **YouTube Transcription**  
   - Paste YouTube URL
   - Click download button

### Command Line Interface
```bash
python main.py
```

1. **Interactive Mode**
```bash
Choose input method:
1. Voice recording
2. File upload
3. URL processing
```

2. **Direct Processing**
```bash
# Process YouTube video
python main.py --url "https://youtube.com/watch?v=..."

# Process local file
python main.py --file input.mp3
```

3. **Advanced Options**
```bash
# Instagram Story (requires credentials)
python main.py --url "instagram-story-url" --username your_username --password your_password

# Batch processing
python main.py --batch file_list.txt
```

## Security

| Feature                | Implementation Details                |
|------------------------|---------------------------------------|
| Credential Storage     | AES-256 encrypted configuration file |
| API Communication      | HTTPS with TLS 1.3                   |
| Session Management     | Ephemeral environment variables      |
| Audio Data Handling    | Local processing only                 |

## Supported Platforms

| Platform       | CLI Support | GUI Support |
|----------------|-------------|-------------|
| YouTube        | ✅          | ✅          |
| TikTok         | ✅          | ⚠️*         |
| Instagram      | ✅          | ⚠️*         |
| Local Files    | ✅          | ✅          |
| Microphone     | ✅          | ✅          |

*GUI support requires custom implementation

## Troubleshooting

Common Issues:
1. **FFmpeg Not Found**  
   Ensure FFmpeg is installed and in system PATH

2. **Audio Recording Issues**  
   Check microphone permissions and PyAudio installation

3. **API Errors**  
   Verify credentials and API endpoint configuration

View detailed logs:
```bash
tail -f output_files/speech_to_text.log
```

## License

MIT License - See [LICENSE](LICENSE) for full text.
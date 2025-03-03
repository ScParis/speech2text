# Speech to Text Transcriber

A multi-platform transcription solution with GUI and CLI interfaces, powered by [@ScParis](https://github.com/ScParis).

## Estrutura do Projeto
```
speech2text/
├── config/         # Configurações do projeto
├── services/       # Serviços principais
├── utils/         # Utilitários
├── gui/           # Interface gráfica
└── output_files/  # Arquivos gerados
```

## Core Capabilities
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

## Usage

### GUI Application
```bash
python main.py
```

1. **Record Audio**  
   - Click microphone icon (🎤)
   - Speak for up to 5 seconds
   - Automatic transcription

2. **Process Files**  
   - Supported formats: MP3, WAV, MP4, WEBM
   - Click upload button (📁)
   - Select audio/video file

3. **YouTube/TikTok/Instagram**  
   - Paste URL in text field
   - Click process button
   - Wait for transcription

### CLI Interface
```bash
python main.py --cli
```

## Configuration

### API Setup
1. Get your Gemini API key
2. Configure via GUI:
   - Click settings icon (⚙️)
   - Enter API key
   - Save configuration

### Security Features
- AES-256 encrypted credentials
- Secure API communication
- Local processing only

## Supported Platforms

| Platform       | Support | Features |
|----------------|---------|----------|
| YouTube        | ✅      | Public/Private videos |
| TikTok         | ✅      | Videos |
| Instagram      | ✅      | Stories/Reels |
| Local Files    | ✅      | Audio/Video |
| Microphone     | ✅      | Live recording |

## Troubleshooting

Common Issues:
1. **FFmpeg Not Found**  
   ```bash
   sudo apt install ffmpeg  # Linux
   choco install ffmpeg    # Windows
   ```

2. **Audio Recording**  
   - Check microphone permissions
   - Verify PyAudio installation

3. **API Errors**  
   - Verify API key
   - Check internet connection

## License

MIT License - See [LICENSE](LICENSE) for details.
# Speech-to-Text Transcriber

A modern and user-friendly application for transcribing audio to text using the Gemini API.

## Features

- 🎤 Audio Recording: Record audio directly from your microphone
- 📁 File Upload: Upload existing audio files for transcription
- 🎥 YouTube Integration: Download and transcribe audio from YouTube videos
- 🔒 Secure Configuration: Encrypted storage of API credentials
- 🎯 Modern Interface: Dark theme with intuitive controls

## Installation

1. Clone the repository:
```bash
git clone https://github.com/paris-sc/proj-speech2text.git
cd speech2text
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Before using the application, you need to configure your Gemini API credentials:

1. Launch the application:
```bash
python gui_app.py
```

2. Click the settings icon (⚙️) in the top-right corner
3. Enter your Gemini API credentials:
   - **API Key**: Your Gemini API authentication key
   - **API URL**: The Gemini API endpoint URL (e.g., https://generativelanguage.googleapis.com)
4. Click "Save" to securely store your credentials

Your credentials will be encrypted and stored securely on your system.

## Usage

### GUI Application

1. Launch the GUI:
```bash
python gui_app.py
```

2. Choose your input method:
   - Click "Record Audio" to record from your microphone
   - Click "Upload Audio File" to transcribe an existing file
   - Paste a YouTube URL and click "Download" to transcribe from YouTube

3. The transcription will appear in the main text area
4. Use "Export Transcription" to save your results

### Command Line Interface

For command-line usage:
```bash
python main.py --help
```

## Security

- API credentials are encrypted using Fernet symmetric encryption
- Credentials are stored securely and never exposed in plaintext
- Environment variables are used for runtime credential management

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/paris-sc/proj-speech2text/issues) on GitHub.

# Testing Speech-to-Text GUI Application

## Prerequisites
- Python 3.8+
- Microphone
- Internet connection
- Gemini API key

## Setup
1. Run setup script:
```bash
./setup.sh
```

2. Activate virtual environment:
```bash
source venv/bin/activate
```

3. Set Gemini API Key:
```bash
export GEMINI_API_KEYVS='your_api_key_here'
```

## Running the Application
```bash
python gui_app.py
```

## Test Scenarios
1. **Microphone Recording**
   - Click "Record Audio"
   - Speak clearly for 10-15 seconds
   - Verify transcription appears

2. **YouTube Audio Download**
   - Paste a YouTube video URL
   - Click "Download"
   - Verify audio downloads and transcribes

3. **File Upload**
   - Click "Upload Audio File"
   - Select a .wav or .mp3 file
   - Verify transcription

4. **Export Transcript**
   - After transcription
   - Click "Export Transcript"
   - Save and verify file contents

## Troubleshooting
- Ensure microphone permissions
- Check internet connectivity
- Verify Gemini API key
- Check console for detailed errors

## Known Limitations
- Limited audio file formats
- Transcription quality depends on audio clarity
- YouTube download may have restrictions

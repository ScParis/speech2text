import sys
import os
import qtawesome as qta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QLineEdit, QMessageBox, QDialog, 
                             QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Import existing project functions
from main import (record_audio, download_audio_from_youtube, 
                  transcribe_audio_gemini, convert_to_mp3)
from config import update_gemini_config  # We'll create this function in config.py

class APIConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Gemini API Configuration')
        self.setModal(True)
        
        # Layout
        layout = QFormLayout()
        
        # API URL Input
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText('Enter Gemini API URL')
        default_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent'
        self.api_url_input.setText(os.getenv('GEMINI_API_URL', default_url))
        layout.addRow('API URL:', self.api_url_input)
        
        # API Key Input
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText('Enter Gemini API Key')
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(os.getenv('GEMINI_API_KEYVS', ''))
        layout.addRow('API Key:', self.api_key_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
    
    def validate_inputs(self):
        """Validate API configuration inputs"""
        api_url = self.api_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        # Basic validation
        if not api_url:
            QMessageBox.warning(self, 'Validation Error', 'API URL cannot be empty')
            return False
        
        if not api_key:
            QMessageBox.warning(self, 'Validation Error', 'API Key cannot be empty')
            return False
        
        # URL validation (basic check)
        if not api_url.startswith('https://'):
            QMessageBox.warning(self, 'Validation Error', 'API URL must start with https://')
            return False
        
        return True
    
    def accept(self):
        """Handle configuration save"""
        # Validate inputs
        if not self.validate_inputs():
            return
        
        # Get configuration values
        api_url = self.api_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        try:
            # Update configuration
            from config import update_gemini_config
            if update_gemini_config(api_url, api_key):
                # Close dialog on successful configuration
                super().accept()
            else:
                QMessageBox.critical(
                    self, 
                    'Configuration Error', 
                    'Failed to save API configuration. Please check your inputs.'
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                'Configuration Error', 
                f'An unexpected error occurred: {str(e)}'
            )

class TranscriptionThread(QThread):
    """Background thread for audio transcription"""
    transcription_complete = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file

    def run(self):
        try:
            # Perform transcription
            # Handle both tuple and string inputs
            if isinstance(self.audio_file, tuple):
                audio_path = self.audio_file[0] if self.audio_file else None
            else:
                audio_path = self.audio_file
            
            # Perform transcription
            result = transcribe_audio_gemini(audio_path)
            
            # Emit the result
            if result is not None:
                self.transcription_complete.emit(result)
            else:
                self.error_occurred.emit("Transcription failed. No result returned.")
        except Exception as e:
            self.error_occurred.emit(str(e))

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Check API configuration on startup
        self.check_api_config()
        
        self.initUI()

    def check_api_config(self):
        """Check if API configuration is set"""
        if not os.getenv('GEMINI_API_KEYVS'):
            QMessageBox.information(
                self, 
                'API Configuration Needed', 
                'Please configure your Gemini API settings before using the app.'
            )
            self.open_api_config()

    def open_api_config(self):
        """Open API configuration dialog"""
        config_dialog = APIConfigDialog(self)
        if config_dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(
                self, 
                'Configuration Saved', 
                'Gemini API settings have been updated successfully.'
            )
        else:
            QMessageBox.warning(
                self, 
                'Configuration Skipped', 
                'You will not be able to use transcription features without API configuration.'
            )

    def initUI(self):
        # Main window setup
        self.setWindowTitle('Speech-to-Text App')
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel('Speech-to-Text Transcriber')
        header.setFont(QFont('Arial', 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # API Configuration
        config_action = QPushButton('API Settings')
        config_action.setIcon(qta.icon('fa.cog', color='white'))
        config_action.clicked.connect(self.open_api_config)
        
        config_layout = QHBoxLayout()
        config_layout.addStretch()
        config_layout.addWidget(config_action)
        main_layout.addLayout(config_layout)
        
        # Audio Input Section
        input_layout = QHBoxLayout()
        
        # Microphone Record Button
        mic_btn = QPushButton('Record Audio')
        mic_btn.setIcon(qta.icon('fa.microphone', color='white'))
        mic_btn.clicked.connect(self.start_microphone_recording)
        input_layout.addWidget(mic_btn)
        
        # YouTube Link Input
        youtube_input = QLineEdit()
        youtube_input.setPlaceholderText('Paste YouTube URL')
        input_layout.addWidget(youtube_input)
        
        # Download YouTube Audio Button
        yt_btn = QPushButton('Download')
        yt_btn.setIcon(qta.icon('fa.download', color='white'))
        yt_btn.clicked.connect(lambda: self.download_youtube_audio(youtube_input.text()))
        input_layout.addWidget(yt_btn)
        
        main_layout.addLayout(input_layout)
        
        # File Upload Button
        file_btn = QPushButton('Upload Audio File')
        file_btn.setIcon(qta.icon('fa.upload', color='white'))
        file_btn.clicked.connect(self.upload_audio_file)
        main_layout.addWidget(file_btn)
        
        # Transcription Display
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)
        main_layout.addWidget(self.transcript_display)
        
        # Export Button
        export_btn = QPushButton('Export Transcript')
        export_btn.setIcon(qta.icon('fa.save', color='white'))
        export_btn.clicked.connect(self.export_transcript)
        main_layout.addWidget(export_btn)
        
        # Set layout
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: none;
                color: white;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
            }
        """)

    def start_microphone_recording(self):
        try:
            audio_file = record_audio()
            self.start_transcription(audio_file)
        except Exception as e:
            QMessageBox.warning(self, 'Recording Error', str(e))

    def download_youtube_audio(self, url):
        try:
            audio_file = download_audio_from_youtube(url)
            self.start_transcription(audio_file)
        except Exception as e:
            QMessageBox.warning(self, 'YouTube Download Error', str(e))

    def upload_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select Audio File', 
            '', 
            'Audio Files (*.wav *.mp3 *.webm)'
        )
        if file_path:
            self.start_transcription(file_path)

    def start_transcription(self, audio_file):
        # Start transcription in a background thread
        self.transcript_thread = TranscriptionThread(audio_file)
        self.transcript_thread.transcription_complete.connect(self.update_transcript)
        self.transcript_thread.error_occurred.connect(self.show_transcription_error)
        self.transcript_thread.start()

    def update_transcript(self, result):
        """Update transcript display with the result"""
        if result:
            self.transcript_display.setPlainText(str(result))
        else:
            self.show_transcription_error("No transcript could be generated.")

    def show_transcription_error(self, error):
        QMessageBox.warning(self, 'Transcription Error', str(error))

    def export_transcript(self):
        transcript = self.transcript_display.toPlainText()
        if not transcript:
            QMessageBox.warning(self, 'Export Error', 'No transcript to export')
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Export Transcript', 
            '', 
            'Text Files (*.txt);;Word Documents (*.docx)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                QMessageBox.information(self, 'Export Successful', 'Transcript exported successfully')
            except Exception as e:
                QMessageBox.warning(self, 'Export Error', str(e))

def main():
    """
    Main entry point for the Speech-to-Text GUI application.
    Handles application initialization and error logging.
    """
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Output to console
            logging.FileHandler('speech2text_gui.log')  # Output to log file
        ]
    )
    
    try:
        app = QApplication(sys.argv)
        ex = SpeechToTextApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Fatal error in main application: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

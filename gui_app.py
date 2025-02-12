import sys
import os
import qtawesome as qta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Import existing project functions
from main import (record_audio, download_audio_from_youtube, 
                  transcribe_audio_gemini, convert_to_mp3)

class TranscriptionThread(QThread):
    """Background thread for audio transcription"""
    transcription_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file

    def run(self):
        try:
            # Perform transcription
            transcript = transcribe_audio_gemini(self.audio_file)
            self.transcription_complete.emit(transcript)
        except Exception as e:
            self.error_occurred.emit(str(e))

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

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

    def update_transcript(self, transcript):
        self.transcript_display.setPlainText(transcript)

    def show_transcription_error(self, error):
        QMessageBox.warning(self, 'Transcription Error', error)

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
    app = QApplication(sys.argv)
    ex = SpeechToTextApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

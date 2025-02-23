"""
Speech-to-Text Transcriber GUI Application

This module provides a modern graphical user interface for the Speech-to-Text transcriber.
It supports multiple input methods including direct audio recording, file upload,
and YouTube video transcription.

Features:
- Modern dark theme interface
- Secure API configuration management
- Real-time audio recording
- Multiple input methods
- Progress feedback
- Export functionality

Classes:
    SpeechToTextApp: The main application window
    ConfigDialog: Dialog for managing API configuration
    AudioRecordThread: Background thread for audio recording
"""

import sys
import os
import time
import logging
import traceback
import qtawesome as qta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                           QFileDialog, QLineEdit, QMessageBox, QComboBox,
                           QProgressBar, QStatusBar, QDialog, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor
import pyaudio
import wave
from config_manager import ConfigManager
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gui_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Importar apenas as funções necessárias da main.py
try:
    from main import (convert_to_mp3, WAVE_OUTPUT_FILENAME, 
                     WAVE_OUTPUT_FILENAME_REDUCED, reduce_sample_rate, 
                     transcribe_audio_gemini, improve_transcript, 
                     MP3_OUTPUT_FILENAME)
    logging.info("Módulos importados com sucesso")
except Exception as e:
    logging.error(f"Erro ao importar módulos: {e}")
    logging.error(traceback.format_exc())
    raise

# Configurações de diretório
OUTPUT_DIR = "output_files"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    logging.info(f"Diretório de saída criado: {OUTPUT_DIR}")

# Audio recording settings
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

class TranscriptionThread(QThread):
    """Thread otimizada para transcrição."""
    transcription_complete = pyqtSignal(str)
    transcription_progress = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file
        logging.info(f"TranscriptionThread inicializada com arquivo: {audio_file}")

    def run(self):
        try:
            # Etapa 1: Reduzir taxa de amostragem
            logging.info("Iniciando redução da taxa de amostragem")
            self.transcription_progress.emit("Reduzindo taxa de amostragem...")
            audio_file_reduced, conversion_time = reduce_sample_rate(self.audio_file, WAVE_OUTPUT_FILENAME_REDUCED, 8000)
            if not audio_file_reduced:
                error_msg = "Falha ao reduzir a taxa de amostragem"
                logging.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            logging.info(f"Taxa de amostragem reduzida com sucesso. Tempo: {conversion_time:.2f}s")
            
            # Etapa 2: Converter para MP3
            logging.info("Iniciando conversão para MP3")
            self.transcription_progress.emit("Convertendo para MP3...")
            audio_file_mp3, conversion_time = convert_to_mp3(audio_file_reduced, MP3_OUTPUT_FILENAME)
            if not audio_file_mp3:
                error_msg = "Falha ao converter para MP3"
                logging.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            logging.info(f"Conversão para MP3 concluída. Tempo: {conversion_time:.2f}s")

            # Etapa 3: Transcrever o áudio
            logging.info("Iniciando transcrição com Gemini")
            self.transcription_progress.emit("Transcrevendo o áudio...")
            transcricao_original, transcription_time = transcribe_audio_gemini(audio_file_mp3)
            
            if not transcricao_original:
                error_msg = "Falha na transcrição do áudio"
                logging.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            logging.info("Transcrição concluída com sucesso")

            # Etapa 4: Melhorar a transcrição
            logging.info("Iniciando aprimoramento da transcrição")
            self.transcription_progress.emit("Aprimorando a transcrição...")
            transcricao_melhorada = improve_transcript(transcricao_original)
            
            if transcricao_melhorada:
                logging.info("Transcrição aprimorada com sucesso")
                self.transcription_complete.emit(transcricao_melhorada)
            else:
                logging.warning("Não foi possível aprimorar a transcrição. Usando versão original.")
                self.transcription_complete.emit(transcricao_original)

        except Exception as e:
            logging.error(f"Erro durante a transcrição: {e}")
            logging.error(traceback.format_exc())
            self.error_occurred.emit(str(e))

class YouTubeDownloadThread(QThread):
    """Thread for handling YouTube downloads."""
    download_complete = pyqtSignal(str)
    download_progress = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        logging.info(f"YouTubeDownloadThread initialized with URL: {url}")

    def run(self):
        try:
            logging.info(f"Starting YouTube download: {self.url}")
            self.download_progress.emit("Downloading audio from YouTube...")
            
            import yt_dlp
            output_file = os.path.join(OUTPUT_DIR, "youtube_audio.mp3")
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        percent = d['_percent_str'].strip()
                        self.download_progress.emit(f"Downloading: {percent}")
                    except:
                        pass

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_file.replace('.mp3', ''),
                'quiet': True,
                'progress_hooks': [progress_hook]
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            logging.info(f"Download completed: {output_file}")
            self.download_complete.emit(output_file)
            
        except Exception as e:
            logging.error(f"Error downloading from YouTube: {e}")
            logging.error(traceback.format_exc())
            self.error_occurred.emit(str(e))

class AudioRecordThread(QThread):
    """Thread for handling audio recording."""
    recording_complete = pyqtSignal(str)
    recording_progress = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False

    def run(self):
        try:
            logging.info("Starting audio recording")
            self.recording_progress.emit("Recording audio...")
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)

            frames = []
            self.is_recording = True

            while self.is_recording:
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Save the recorded audio
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            logging.info("Audio recording completed")
            self.recording_complete.emit(WAVE_OUTPUT_FILENAME)

        except Exception as e:
            logging.error(f"Error during audio recording: {e}")
            logging.error(traceback.format_exc())
            self.error_occurred.emit(str(e))

    def stop_recording(self):
        self.is_recording = False

class ConfigDialog(QDialog):
    """
    Dialog for managing API configuration.
    
    This dialog provides a secure interface for users to input and manage their
    Gemini API credentials. All credentials are encrypted before storage.
    
    Features:
    - Secure password input for API key
    - Input validation
    - Encrypted storage
    - Modern dark theme styling
    
    Attributes:
        config_manager (ConfigManager): Instance of ConfigManager for handling credentials
        api_key_input (QLineEdit): Secure input field for API key
        api_url_input (QLineEdit): Input field for API URL
    """
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('API Configuration')
        self.setModal(True)
        layout = QFormLayout()
        
        # API Key input with label
        api_key_label = QLabel('Gemini API Key:')
        api_key_label.setStyleSheet('color: white;')
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText('Enter your Gemini API key here')
        layout.addRow(api_key_label, self.api_key_input)
        
        # API URL input with label
        api_url_label = QLabel('Gemini API URL:')
        api_url_label.setStyleSheet('color: white;')
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText('Enter the Gemini API URL (e.g., https://generativelanguage.googleapis.com)')
        layout.addRow(api_url_label, self.api_url_input)
        
        # Load existing configuration
        config = self.config_manager.load_config()
        if config.get('GEMINI_API_KEY'):
            self.api_key_input.setText(config['GEMINI_API_KEY'])
        if config.get('GEMINI_API_URL'):
            self.api_url_input.setText(config['GEMINI_API_URL'])
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_config)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        # Dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 8px;
                min-width: 300px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
        self.setLayout(layout)

    def save_config(self):
        """Save the configuration securely."""
        config_data = {
            'GEMINI_API_KEY': self.api_key_input.text(),
            'GEMINI_API_URL': self.api_url_input.text()
        }
        
        if self.config_manager.save_config(config_data):
            QMessageBox.information(self, 'Success', 'Configuration saved successfully!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to save configuration')

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recording_thread = None
        self.config_manager = ConfigManager()
        self.initUI()
        
        # Load configuration on startup
        self.config_manager.load_config()

    def initUI(self):
        # Main window setup
        self.setWindowTitle('Speech-to-Text App')
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header with Settings Button
        header_layout = QHBoxLayout()
        header = QLabel('Speech-to-Text Transcriber')
        header.setFont(QFont('Arial', 18, QFont.Bold))
        header_layout.addWidget(header)
        
        settings_btn = QPushButton()
        settings_btn.setIcon(qta.icon('fa.cog', color='white'))
        settings_btn.setToolTip('Configure API Settings')
        settings_btn.clicked.connect(self.show_config_dialog)
        settings_btn.setFixedSize(40, 40)
        header_layout.addWidget(settings_btn)
        
        main_layout.addLayout(header_layout)

        # Record Audio Button
        record_btn = QPushButton('Record Audio')
        record_btn.setIcon(qta.icon('fa.microphone', color='white'))
        record_btn.clicked.connect(self.toggle_recording)
        main_layout.addWidget(record_btn)
        self.record_btn = record_btn
        
        # YouTube Link Input
        url_layout = QHBoxLayout()
        self.youtube_url_input = QLineEdit()
        self.youtube_url_input.setPlaceholderText('Paste YouTube URL here')
        url_layout.addWidget(self.youtube_url_input)
        
        # Download Button
        download_btn = QPushButton('Download')
        download_btn.setIcon(qta.icon('fa.download', color='white'))
        download_btn.clicked.connect(self.download_youtube)
        url_layout.addWidget(download_btn)
        
        main_layout.addLayout(url_layout)
        
        # File Upload Button
        file_btn = QPushButton('Upload Audio File')
        file_btn.setIcon(qta.icon('fa.upload', color='white'))
        file_btn.clicked.connect(self.upload_audio_file)
        main_layout.addWidget(file_btn)
        
        # Progress Label
        self.progress_label = QLabel('Status: Ready')
        main_layout.addWidget(self.progress_label)
        
        # Transcription Display
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)
        self.transcript_display.setPlaceholderText("Transcription will appear here...")
        main_layout.addWidget(self.transcript_display)
        
        # Export Button
        export_btn = QPushButton('Export Transcription')
        export_btn.setIcon(qta.icon('fa.save', color='white'))
        export_btn.clicked.connect(self.export_transcript)
        main_layout.addWidget(export_btn)
        
        # Set layout
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #888888;
            }
            QTextEdit, QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 8px;
            }
            QLabel {
                color: white;
            }
        """)

    def toggle_recording(self):
        """Toggles audio recording on/off"""
        if not self.recording_thread or not self.recording_thread.is_recording:
            # Start recording
            self.record_btn.setText('Stop Recording')
            self.record_btn.setIcon(qta.icon('fa.stop', color='red'))
            self.disable_buttons()
            self.record_btn.setEnabled(True)  # Keep record button enabled
            
            self.recording_thread = AudioRecordThread()
            self.recording_thread.recording_complete.connect(self.recording_finished)
            self.recording_thread.recording_progress.connect(self.update_progress)
            self.recording_thread.error_occurred.connect(self.handle_error)
            self.recording_thread.start()
            
        else:
            # Stop recording
            self.record_btn.setText('Record Audio')
            self.record_btn.setIcon(qta.icon('fa.microphone', color='white'))
            self.recording_thread.stop_recording()

    def recording_finished(self, audio_file):
        """Handles completion of audio recording"""
        self.enable_buttons()
        self.start_transcription(audio_file)

    def download_youtube(self):
        """Downloads audio from YouTube"""
        try:
            url = self.youtube_url_input.text().strip()
            if not url:
                self.show_error("Por favor, insira uma URL do YouTube")
                return
            
            # Clear output directory before starting new download
            self.clear_output_directory()
            
            self.disable_buttons()
            self.update_progress("Iniciando download do YouTube...")
            
            logging.info("Creating YouTube download thread")
            self.download_thread = YouTubeDownloadThread(url)
            self.download_thread.download_complete.connect(self.download_finished)
            self.download_thread.download_progress.connect(self.update_progress)
            self.download_thread.error_occurred.connect(self.handle_error)
            
            logging.info("Starting YouTube download thread")
            self.download_thread.start()
            
        except Exception as e:
            self.show_error(f"Erro ao iniciar download: {str(e)}")
            self.enable_buttons()
            logging.error(f"Erro ao iniciar download: {e}")
            logging.error(traceback.format_exc())

    def start_transcription(self, audio_file):
        """Starts the transcription process."""
        try:
            self.disable_buttons()
            self.update_progress("Iniciando transcrição...")
            self.transcription_thread = TranscriptionThread(audio_file)
            self.transcription_thread.transcription_complete.connect(self.transcription_finished)
            self.transcription_thread.transcription_progress.connect(self.update_progress)
            self.transcription_thread.error_occurred.connect(self.handle_error)
            self.transcription_thread.start()
            logging.info(f"Iniciando transcrição do arquivo: {audio_file}")
        except Exception as e:
            self.show_error(f"Erro ao iniciar transcrição: {str(e)}")
            self.enable_buttons()
            logging.error(f"Erro ao iniciar transcrição: {e}")
            logging.error(traceback.format_exc())

    def clear_output_directory(self):
        """Remove todos os arquivos do diretório de saída."""
        try:
            if os.path.exists(OUTPUT_DIR):
                for file in os.listdir(OUTPUT_DIR):
                    file_path = os.path.join(OUTPUT_DIR, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            os.rmdir(file_path)
                    except Exception as e:
                        logging.error(f"Error clearing output directory: {e}")
                        logging.error(traceback.format_exc())
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)
            logging.info(f"Diretório de saída limpo: {OUTPUT_DIR}")
        except Exception as e:
            logging.error(f"Erro ao limpar diretório de saída: {e}")

    def disable_buttons(self):
        """Disables interactive buttons during processing"""
        for button in self.findChildren(QPushButton):
            button.setEnabled(False)
        self.youtube_url_input.setEnabled(False)

    def enable_buttons(self):
        """Re-enables interactive buttons after processing"""
        for button in self.findChildren(QPushButton):
            button.setEnabled(True)
        self.youtube_url_input.setEnabled(True)

    def update_progress(self, message):
        """Updates progress message in status bar"""
        self.statusBar.showMessage(message)
        QApplication.processEvents()  # Ensure GUI updates are processed

    def transcription_finished(self, transcript):
        """Handles completion of transcription"""
        self.transcript_display.setPlainText(transcript)
        self.statusBar.showMessage("Transcription completed")
        self.enable_buttons()

    def handle_error(self, error):
        """Handles errors during processing"""
        logging.error(f"Error displayed to user: {error}")
        QMessageBox.warning(self, 'Error', error)
        self.statusBar.showMessage("Error during processing")
        self.enable_buttons()

    def show_error(self, error):
        """Displays error message"""
        logging.error(f"Error displayed to user: {error}")
        QMessageBox.warning(self, 'Error', error)
        self.statusBar.showMessage("Error during processing")

    def export_transcript(self):
        """Exports transcription to a file"""
        transcript = self.transcript_display.toPlainText()
        if not transcript:
            QMessageBox.warning(self, 'Export Error', 'No transcription to export')
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Export Transcription', 
            '', 
            'Text Files (*.txt)'
        )
        
        if file_path:
            try:
                logging.info(f"Exporting transcription to: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                QMessageBox.information(self, 'Export Completed', 'Transcription exported successfully')
            except Exception as e:
                logging.error(f"Error exporting transcription: {e}")
                logging.error(traceback.format_exc())
                QMessageBox.warning(self, 'Export Error', str(e))

    def show_config_dialog(self):
        """Show the configuration dialog."""
        dialog = ConfigDialog(self.config_manager, self)
        dialog.exec_()

    def download_finished(self, audio_file):
        """Called when YouTube download is complete."""
        logging.info(f"Download completed: {audio_file}")
        if os.path.exists(audio_file):
            self.start_transcription(audio_file)
        else:
            self.show_error("Arquivo de áudio não encontrado após download")
            self.enable_buttons()

    def upload_audio_file(self):
        """Permite o upload de arquivos de áudio."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 'Selecione o arquivo',
                '',
                'Arquivos de Áudio (*.wav *.mp3)'
            )
            if file_path:
                logging.info(f"Arquivo selecionado: {file_path}")
                self.clear_output_directory()
                self.start_transcription(file_path)
        except Exception as e:
            self.show_error(f"Erro ao carregar arquivo de áudio: {str(e)}")
            logging.error(f"Erro ao carregar arquivo de áudio: {e}")
            logging.error(traceback.format_exc())

def clear_output_directory():
    """Clears the output directory before starting the application."""
    for file in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            logging.error(f"Error clearing output directory: {e}")
            logging.error(traceback.format_exc())

def main():
    """Main function to start the GUI application."""
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # Clear output directory before starting
    clear_output_directory()
    logging.info("Starting GUI application")
    main()

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
import logging
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QLabel, QTextEdit, QFileDialog, QProgressBar,
                           QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox,
                           QHBoxLayout, QGroupBox, QSplitter, QFrame,
                           QStatusBar, QToolButton, QStyleFactory)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize  # Adicionado QSize
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont

# Adiciona o diretório raiz ao PYTHONPATH
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from services.audio_service import (
    record_audio,
    download_audio_from_youtube,
    download_tiktok_video,
    download_instagram_story
)
from services.transcription_service import process_and_analyze_transcription
from utils.validators import validate_audio_file, validate_video_file, identify_platform
from utils.file_manager import clear_output_directory
from config.config import setup_logging, OUTPUT_DIR, save_api_key, load_api_key, update_api_key

class TranscriptionWorker(QThread):
    finished = pyqtSignal(tuple)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file

    def run(self):
        try:
            self.progress.emit("Iniciando transcrição...")
            result = process_and_analyze_transcription(self.audio_file)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class ApiConfigDialog(QDialog):
    """Diálogo para configurar a chave API"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração da API")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # Campo da chave API
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        current_key = load_api_key()
        if current_key:
            self.api_key_input.setText(current_key)
        
        layout.addRow("Chave API Gemini:", self.api_key_input)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_api_key(self):
        return self.api_key_input.text().strip()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech to Text Transcriber")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                border: 2px solid #cccccc;
                border-radius: 6px;
                margin-top: 1em;
                padding: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                background-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
            }
            QStatusBar {
                background-color: #f5f5f5;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Barra de ferramentas superior
        toolbar_group = QGroupBox("Ferramentas")
        toolbar_layout = QHBoxLayout()
        
        # Botões com ícones
        self.config_button = self.create_tool_button("⚙️", "Configurar API")
        self.record_button = self.create_tool_button("🎤", "Gravar Áudio")
        self.file_button = self.create_tool_button("📁", "Selecionar Arquivo")
        
        toolbar_layout.addWidget(self.config_button)
        toolbar_layout.addWidget(self.record_button)
        toolbar_layout.addWidget(self.file_button)
        toolbar_layout.addStretch()
        toolbar_group.setLayout(toolbar_layout)

        # Área de entrada de URL
        url_group = QGroupBox("URL do Vídeo")
        url_layout = QHBoxLayout()
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("Cole a URL do YouTube, TikTok ou Instagram aqui...")
        self.url_input.setMaximumHeight(70)
        self.url_button = QPushButton("Processar URL")
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.url_button)
        url_group.setLayout(url_layout)

        # Área de resultados
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()
        self.transcription_output = QTextEdit()
        self.transcription_output.setReadOnly(True)
        results_layout.addWidget(self.transcription_output)
        results_group.setLayout(results_layout)

        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_label = QLabel("Pronto")
        self.status_bar.addWidget(self.status_label)

        # Adiciona widgets ao layout principal
        main_layout.addWidget(toolbar_group)
        main_layout.addWidget(url_group)
        main_layout.addWidget(results_group)

        # Conecta sinais
        self.config_button.clicked.connect(self.show_config_dialog)
        self.record_button.clicked.connect(self.handle_record)
        self.file_button.clicked.connect(self.handle_file)
        self.url_button.clicked.connect(self.handle_url)

        # Configuração inicial
        setup_logging()
        clear_output_directory()
        
        # Verificar chave API no início
        if not load_api_key():
            self.show_config_dialog()

    def create_tool_button(self, icon_text, tooltip):
        """Cria um botão de ferramenta estilizado"""
        button = QToolButton()
        button.setText(icon_text)
        button.setToolTip(tooltip)
        button.setMinimumSize(QSize(40, 40))
        button.setFont(QFont('Arial', 14))
        return button

    def handle_record(self):
        try:
            self.status_label.setText("Gravando áudio...")
            audio_file = record_audio()
            if audio_file:
                self.process_audio(audio_file)
        except Exception as e:
            self.show_error(f"Erro na gravação: {e}")

    def handle_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo", "", 
            "Arquivos de Áudio/Vídeo (*.mp3 *.wav *.m4a *.mp4 *.avi *.mkv)"
        )
        if file_path and (validate_audio_file(file_path) or validate_video_file(file_path)):
            self.process_audio(file_path)
        elif file_path:
            self.show_error("Arquivo inválido")

    def handle_url(self):
        url = self.url_input.toPlainText().strip()
        platform = identify_platform(url)
        if not platform:
            self.show_error("URL não suportada")
            return

        self.status_label.setText("Baixando áudio...")
        try:
            if platform == "YouTube":
                audio_file, _ = download_audio_from_youtube(url)
            elif platform == "TikTok":
                video_file, _ = download_tiktok_video(url)
                audio_file, _ = self.extract_audio(video_file)
            elif platform in ["Instagram Story", "Instagram Reel"]:
                video_file, _ = download_instagram_story(url)
                audio_file, _ = self.extract_audio(video_file)
            else:
                self.show_error("Plataforma não suportada")
                return

            if audio_file:
                self.process_audio(audio_file)
            else:
                self.show_error("Falha ao processar áudio")
        except Exception as e:
            self.show_error(f"Erro no processamento: {e}")

    def process_audio(self, audio_file):
        self.worker = TranscriptionWorker(audio_file)
        self.worker.finished.connect(self.handle_results)
        self.worker.error.connect(self.show_error)
        self.worker.progress.connect(self.update_status)
        self.worker.start()

    def handle_results(self, results):
        transcricao, transcricao_melhorada, analise = results
        output_text = ""
        
        if transcricao:
            output_text += "Transcrição Original:\n" + transcricao + "\n\n"
        
        if transcricao_melhorada:
            output_text += "Transcrição Melhorada:\n" + transcricao_melhorada + "\n\n"
        
        if analise:
            output_text += "Análise e Percepções:\n" + analise

        self.transcription_output.setText(output_text)
        self.status_label.setText("Processamento concluído")

    def show_error(self, message):
        """Mostra erro na barra de status"""
        self.status_label.setText(f"Erro: {message}")
        self.status_label.setStyleSheet("color: #f44336;")  # Vermelho
        logging.error(message)

    def update_status(self, message):
        """Atualiza a mensagem de status"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("")  # Reset color

    def show_config_dialog(self):
        dialog = ApiConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            api_key = dialog.get_api_key()
            if api_key:
                update_api_key(api_key)  # Usar nova função
                self.status_label.setText("Chave API configurada com sucesso")
            else:
                QMessageBox.warning(
                    self,
                    "Erro",
                    "Por favor, forneça uma chave API válida"
                )
                self.show_config_dialog()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Configurar logging antes de criar a janela
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    setup_logging()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

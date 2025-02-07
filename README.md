# Speech-to-Text Application

## Description
Este projeto é uma aplicação de transcrição de áudio que utiliza a API Gemini para converter gravações de áudio em texto. Ele permite gravar áudio do microfone, baixar áudio de vídeos do YouTube e processar arquivos de áudio para transcrição.

## Features
- Gravação de áudio do microfone e salvamento em formato WAV.
- Download de áudio de vídeos do YouTube.
- Redução da taxa de amostragem de arquivos de áudio.
- Conversão de arquivos de áudio para MP3.
- Transcrição de áudio utilizando a API Gemini.
- Identificação de personagens e formatação da transcrição.

## Requirements
- Python 3.x
- Bibliotecas:
  - requests
  - pyaudio
  - wave
  - yt-dlp
  - tqdm
  - ffmpeg

## Installation
1. Clone o repositório:
   ```bash
   git clone <your-repo-url>
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd speech2text
   ```
3. Crie um ambiente virtual e ative-o:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Execute o script principal:
   ```bash
   python to_text.py
   ```
2. Siga as instruções no terminal para gravar áudio ou fornecer um link do YouTube.

## Contributing
Contribuições são bem-vindas! Sinta-se à vontade para abrir um pull request ou relatar problemas.

## License
Este projeto está licenciado sob a MIT License.

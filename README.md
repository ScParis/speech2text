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
   git clone https://github.com/ScParis/speech2text.git
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

## Configuração da API Gemini
Para utilizar a API Gemini, você precisa de uma chave de API. Siga os passos abaixo:
1. Acesse o site da API Gemini e registre-se para obter uma chave de API.
2. Adicione a chave de API ao arquivo `config.py` como `GEMINI_API_KEY`.

## Dependências Adicionais
Além das bibliotecas listadas, você pode precisar instalar o `ffmpeg` para conversão de áudio. Você pode instalá-lo usando:
```bash
sudo apt-get install ffmpeg
```

## Usage
1. Execute o script principal:
   ```bash
   python to_text.py
   ```
2. Siga as instruções no terminal para gravar áudio ou fornecer um link do YouTube.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou relatar problemas. Para contribuir:
1. Fork o repositório.
2. Crie uma nova branch para suas alterações.
3. Envie um pull request com uma descrição clara das suas mudanças.

## Problemas Comuns
Aqui estão alguns problemas comuns e suas soluções:
- **Erro de gravação de áudio**: Verifique se o microfone está conectado e configurado corretamente nas configurações do sistema.
- **Problemas de instalação de dependências**: Certifique-se de que o `pip` e o `python` estão atualizados e que você está usando um ambiente virtual.

## License
Este projeto está licenciado sob a MIT License.

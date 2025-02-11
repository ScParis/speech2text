# Speech-to-Text Application

## Descrição
Aplicação de transcrição de áudio que utiliza a API Gemini para converter gravações em texto, com suporte para:
- Gravação de áudio do microfone
- Download de áudio do YouTube
- Transcrição de arquivos de áudio

## Requisitos
- Python 3.x
- Dependências: 
  ```
  requests, pyaudio, yt-dlp, tqdm, 
  ffmpeg-python, google-auth, google-generativeai
  ```
- `ffmpeg` instalado no sistema

## Instalação Rápida
1. Clone o repositório:
   ```bash
   git clone https://github.com/ScParis/speech2text.git
   cd speech2text
   ```

2. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração
1. Obtenha uma chave de API do Gemini
2. Configure a variável de ambiente:
   ```bash
   export GEMINI_API_KEY='sua_chave_aqui'
   ```

## Uso
```bash
python to_text.py
```
Siga as instruções no terminal para:
- Gravar áudio do microfone
- Carregar arquivo de áudio
- Inserir link do YouTube

## Contribuição
- Faça um fork do repositório
- Crie uma branch para suas alterações
- Envie um pull request

## Licença
MIT - Use por sua conta e risco.

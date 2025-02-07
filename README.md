# Speech-to-Text Application

### Description
Este projeto é uma aplicação de transcrição de áudio que utiliza a API Gemini para converter gravações de áudio em texto. Ele permite gravar áudio do microfone, baixar áudio de vídeos do YouTube e processar arquivos de áudio para transcrição.

### Features
- Gravação de áudio do microfone e salvamento em formato WAV.
- Download de áudio de vídeos do YouTube.
- Redução da taxa de amostragem de arquivos de áudio.
- Conversão de arquivos de áudio para MP3.
- Transcrição de áudio utilizando a API Gemini.
- Identificação de personagens e formatação da transcrição.

### Requirements
- Python 3.x
- Bibliotecas:
  - requests
  - pyaudio
  - yt-dlp
  - tqdm
  - ffmpeg-python
  - google-auth

### Installation
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

### Configuração do arquivo config.py

Para utilizar a API Gemini, você deve configurar o arquivo `config.py`. Agora, o arquivo utiliza uma variável de ambiente para armazenar a chave da API.

### Variáveis de Ambiente

1. Defina a variável de ambiente `GEMINI_API_KEYVS` com sua chave da API Gemini.

   No terminal, você pode definir a variável de ambiente com o seguinte comando:
   ```bash
   export GEMINI_API_KEYVS='sua_chave_aqui'
   ```

2. Certifique-se de que o arquivo `config.py` está configurado para usar essa variável de ambiente.

### Dependências Adicionais
Além das bibliotecas listadas, você pode precisar instalar o `ffmpeg` para conversão de áudio. Você pode instalá-lo usando:
```bash
sudo apt-get install ffmpeg
```

### Instruções Detalhadas de Uso

1. **Clone o Repositório**:  
   Primeiro, clone o repositório usando o comando:
   ```bash
   git clone https://github.com/ScParis/speech2text.git
   ```

2. **Navegue até o Diretório do Projeto**:  
   Entre no diretório do projeto:
   ```bash
   cd speech2text
   ```

3. **Crie e Ative um Ambiente Virtual**:  
   Crie um ambiente virtual para gerenciar as dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instale as Dependências**:  
   Instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configuração do Arquivo `config.py`**:  
   - Defina a variável de ambiente `GEMINI_API_KEYVS` com sua chave da API Gemini:
     ```bash
     export GEMINI_API_KEYVS='sua_chave_aqui'
     ```
   - Certifique-se de que o arquivo `config.py` está configurado para usar essa variável de ambiente.

6. **Executar o Aplicativo**:  
   Para iniciar a aplicação, execute o script principal:
   ```bash
   python to_text.py
   ```

7. **Escolha uma Opção**:  
   Você será solicitado a escolher uma opção:
   - Gravar áudio do microfone
   - Fornecer o caminho para um arquivo de áudio existente
   - Fornecer um link do YouTube

8. **Siga as Instruções no Terminal**:  
   Dependendo da opção escolhida, siga as instruções exibidas no terminal para interagir com o aplicativo.

### Usage
1. Execute o script principal:
   ```bash
   python to_text.py
   ```
2. Siga as instruções no terminal para gravar áudio ou fornecer um link do YouTube.

### Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou relatar problemas. Para contribuir:
1. Fork o repositório.
2. Crie uma nova branch para suas alterações.
3. Envie um pull request com uma descrição clara das suas mudanças.

### Problemas Comuns
Aqui estão alguns problemas comuns e suas soluções:
- **Erro de gravação de áudio**: Verifique se o microfone está conectado e configurado corretamente nas configurações do sistema.
- **Problemas de instalação de dependências**: Certifique-se de que o `pip` e o `python` estão atualizados e que você está usando um ambiente virtual.

### License
Este projeto está licenciado sob a MIT License.

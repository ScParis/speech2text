# 🎙️ Speech-to-Text Converter

## 🌟 Visão Geral do Projeto

O Speech-to-Text Converter é uma solução avançada de transcrição de áudio que utiliza inteligência artificial para transformar diferentes fontes de áudio em texto preciso e formatado.

### 🚀 Principais Características

- **Múltiplas Fontes de Entrada**:
  - Gravação direta do microfone
  - Carregamento de arquivos de áudio locais
  - Download de áudio de plataformas como YouTube (vídeos, músicas, shorts)

- **Processamento Inteligente**:
  - Redução da taxa de amostragem para otimização
  - Conversão automática para formatos compatíveis
  - Transcrição utilizando API Gemini

- **Recursos Avançados**:
  - Correção gramatical e ortográfica
  - Identificação de diferentes locutores
  - Formatação inteligente do texto transcrito

## 🛠 Tecnologias Utilizadas

- **Linguagem**: Python 3.x
- **Processamento de Áudio**: 
  - PyAudio
  - FFmpeg
- **Download de Vídeo**: yt-dlp
- **Inteligência Artificial**: 
  - Google Generative AI (Gemini)
  - Processamento de linguagem natural

## 📦 Dependências

- requests
- pyaudio
- yt-dlp
- tqdm
- ffmpeg-python
- google-auth
- google-generativeai

## 🔧 Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/ScParis/speech2text.git
cd speech2text

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar FFmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

## 🔐 Configuração

1. Obtenha uma chave de API do Google Generative AI (Gemini)
2. Configure a variável de ambiente:
   ```bash
   export GEMINI_API_KEY='sua_chave_aqui'
   ```

## 🚀 Uso Rápido

```bash
# Executar o aplicativo
python main.py

# Opções disponíveis:
# 1. Gravar áudio do microfone
# 2. Carregar arquivo de áudio local
# 3. Baixar áudio do YouTube
```

## 🤝 Como Contribuir

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## 🐛 Solução de Problemas Comuns

- **Erro de Gravação de Áudio**: 
  - Verifique as configurações do microfone
  - Garanta permissões de acesso ao dispositivo de áudio

- **Problemas com Dependências**:
  - Use sempre um ambiente virtual
  - Mantenha o pip e as dependências atualizadas

- **Erros na Transcrição**:
  - Verifique a qualidade do áudio de entrada
  - Certifique-se de ter uma conexão estável com a internet
  - Confirme a validade da chave da API Gemini

## 📊 Métricas e Performance

- Suporta áudios de até 10 minutos
- Tempo médio de transcrição: 30-60 segundos
- Precisão de transcrição: ~90% (variável conforme qualidade do áudio)

## 📄 Licença

Distribuído sob a Licença MIT. Veja `LICENSE` para mais informações.

## 🌐 Contato

Desenvolvido com ❤️ @scparis

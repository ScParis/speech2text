# Documentação do Projeto Speech-to-Text

## Introdução
Este projeto é uma aplicação de transcrição de áudio que utiliza a API Gemini para converter gravações de áudio em texto. Ele permite gravar áudio do microfone, baixar áudio de vídeos do YouTube e processar arquivos de áudio para transcrição.

## Instalação
Para instalar e executar o projeto, siga os passos abaixo:

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

## Uso
Para usar a aplicação, execute o script principal:
```bash
python main.py
```
Siga as instruções no terminal para gravar áudio ou fornecer um link do YouTube.

## Funcionalidades
- Gravação de áudio do microfone e salvamento em formato WAV.
- Download de áudio de vídeos do YouTube.
- Redução da taxa de amostragem de arquivos de áudio.
- Conversão de arquivos de áudio para MP3.
- Transcrição de áudio utilizando a API Gemini.
- Identificação de personagens e formatação da transcrição.

## Testes
Para garantir que o código funcione corretamente, é recomendável implementar testes automatizados. Você pode usar bibliotecas como `unittest` ou `pytest` para criar testes para suas funções.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou relatar problemas. Para contribuir:
1. Fork o repositório.
2. Crie uma nova branch para suas alterações.
3. Envie um pull request com uma descrição clara das suas mudanças.

## Licença
Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.

## Referências
- [API Gemini](https://gemini.example.com)
- [Documentação do Python](https://docs.python.org/3/)

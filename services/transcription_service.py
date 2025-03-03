import os
import requests
import json
import base64
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.config import GEMINI_API_KEY, GEMINI_API_URL, GEMINI_CONFIG
from .audio_processing import split_audio, combine_texts

def process_transcription(audio_file):
    """Processa a transcrição do áudio usando threads"""
    try:
        audio_chunks = split_audio(audio_file, max_size_mb=GEMINI_CONFIG["chunk_size_mb"])
        if not audio_chunks:
            logging.error("Falha ao dividir o áudio em chunks")
            return None

        # Usando ThreadPoolExecutor para processamento paralelo
        with ThreadPoolExecutor(max_workers=GEMINI_CONFIG["max_workers"]) as executor:
            # Submete todos os chunks para processamento
            future_to_chunk = {
                executor.submit(transcribe_chunk, chunk): i 
                for i, chunk in enumerate(audio_chunks, 1)
            }

            transcriptions = [None] * len(audio_chunks)
            for future in as_completed(future_to_chunk):
                chunk_index = future_to_chunk[future]
                try:
                    result = future.result()
                    if result:
                        transcriptions[chunk_index - 1] = result
                        logging.info(f"Chunk {chunk_index} processado com sucesso")
                    else:
                        logging.error(f"Falha ao processar chunk {chunk_index}")
                except Exception as e:
                    logging.error(f"Erro no chunk {chunk_index}: {e}")

        # Filtra chunks que falharam
        transcriptions = [t for t in transcriptions if t]
        
        if not transcriptions:
            logging.error("Nenhum chunk foi transcrito com sucesso")
            return None

        return combine_texts(transcriptions)
    except Exception as e:
        logging.error(f"Erro no processamento da transcrição: {e}")
        return None

def transcribe_chunk(audio_file):
    """Transcreve um chunk de áudio"""
    retries = 0
    last_error = None
    
    while retries < GEMINI_CONFIG["max_retries"]:
        try:
            with open(audio_file, "rb") as f:
                audio_data = f.read()
            
            audio_encoded = base64.b64encode(audio_data).decode("utf-8")
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "Transcreva este áudio para texto em português brasileiro."
                    }, {
                        "inlineData": {
                            "mimeType": "audio/mpeg",
                            "data": audio_encoded
                        }
                    }]
                }]
            }

            response = requests.post(
                GEMINI_API_URL,
                headers=GEMINI_CONFIG["headers"],
                json=payload,
                timeout=GEMINI_CONFIG["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and result["candidates"]:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
            
            last_error = response.text
            
        except Exception as e:
            last_error = str(e)
            
        retries += 1
        if retries < GEMINI_CONFIG["max_retries"]:
            time.sleep(2 ** retries)

    logging.error(f"Falha após {retries} tentativas. Último erro: {last_error}")
    return None

def transcribe_audio_gemini(audio_file):
    """Transcreve um arquivo de áudio usando a API Gemini."""
    try:
        with open(audio_file, "rb") as f:
            audio_data = f.read()

        # Codifica o áudio em Base64
        audio_encoded = base64.b64encode(audio_data).decode("utf-8")

        payload = {
            "contents": [{
                "parts": [{
                    "text": "Transcreva o áudio com precisão."
                }, {
                    "inlineData": {
                        "mimeType": "audio/mpeg",
                        "data": audio_encoded
                    }
                }]
            }]
        }

        response = requests.post(
            GEMINI_API_URL, 
            json=payload,
            headers=GEMINI_CONFIG["headers"],
            timeout=GEMINI_CONFIG["timeout"]
        )
        
        if response.status_code != 200:
            logging.error(f"Erro na API Gemini: {response.status_code} - {response.text}")
            return None

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        logging.error(f"Erro na transcrição: {e}")
        return None

def improve_transcript(transcricao_original):
    """Melhora a transcrição usando Gemini"""
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""Corrija a ortografia e gramática do texto a seguir, 
                    mantendo o significado original e preservando os diálogos:
                    {transcricao_original}"""
                }]
            }]
        }

        response = requests.post(
            GEMINI_API_URL,
            json=payload,
            headers=GEMINI_CONFIG["headers"],
            timeout=GEMINI_CONFIG["timeout"]
        )

        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]

        logging.error(f"Erro na API Gemini: {response.text}")
        return None

    except Exception as e:
        logging.error(f"Erro na melhoria da transcrição: {e}")
        return None

def generate_summary_and_insights(transcricao_melhorada):
    """Gera um resumo e percepções do texto transcrito"""
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""
                    Analise o seguinte texto e forneça:
                    1. Um resumo conciso em 2-3 frases
                    2. Pontos principais (máximo 3)
                    3. Tom geral da conversa (formal/informal, emotivo/neutro, etc.)
                    4. Percepções adicionais relevantes

                    Texto para análise:
                    {transcricao_melhorada}
                    """
                }]
            }]
        }

        response = requests.post(
            GEMINI_API_URL,
            json=payload,
            headers=GEMINI_CONFIG["headers"],
            timeout=GEMINI_CONFIG["timeout"]
        )

        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]

        logging.error(f"Erro na API Gemini durante análise: {response.text}")
        return None

    except Exception as e:
        logging.error(f"Erro ao gerar resumo e percepções: {e}")
        return None

def process_and_analyze_transcription(audio_file):
    """Processa a transcrição completa incluindo análise"""
    try:
        # Transcrição inicial
        transcricao = transcribe_audio_gemini(audio_file)
        if not transcricao:
            return None, None, None
        
        # Melhoria da transcrição
        transcricao_melhorada = improve_transcript(transcricao)
        if not transcricao_melhorada:
            transcricao_melhorada = transcricao
        
        # Geração de análise
        analise = generate_summary_and_insights(transcricao_melhorada)
        
        return transcricao, transcricao_melhorada, analise
        
    except Exception as e:
        logging.error(f"Erro no processamento completo: {e}")
        return None, None, None

def generate_summary_and_insights(text):
    """Gera um resumo e percepções do texto"""
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""
                    Analise o seguinte texto e forneça:
                    1. Um breve resumo (2-3 frases)
                    2. Principais pontos (máximo 3)
                    3. Tom da conversa/conteúdo
                    4. Insights adicionais relevantes

                    Texto para análise:
                    {text}
                    """
                }]
            }]
        }

        response = requests.post(
            GEMINI_API_URL,
            json=payload,
            headers=GEMINI_CONFIG["headers"],
            timeout=GEMINI_CONFIG["timeout"]
        )

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                return result["candidates"][0]["content"]["parts"][0]["text"]

        logging.error(f"Erro na análise: {response.text}")
        return None

    except Exception as e:
        logging.error(f"Erro ao gerar análise: {e}")
        return None

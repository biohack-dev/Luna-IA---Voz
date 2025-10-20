# -*- coding: utf-8 -*-

import speech_recognition as sr
import requests
import json
import os
import subprocess
import urllib.parse
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import aiml
import warnings
from playsound import playsound
import time

# Suprimir warnings de depreciação
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configurações
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"
WORLD_NEWS_URL = "https://news.google.com/rss/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JYQjBMVUpTR2dKQ1VpZ0FQAQ?hl=pt-BR&gl=BR&ceid=BR%3Apt-419"

# Inicialização do kernel AIML
kernel = aiml.Kernel()
kernel.verbose(False)

# Patch para resolver problema do time.clock no AIML (Python 3.8+)
if not hasattr(time, 'clock'):
    time.clock = time.time

# Carregar AIML de forma segura
def load_aiml():
    try:
        # Tenta carregar o arquivo de startup
        if os.path.exists("std-startup.xml"):
            kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
        else:
            # Se o arquivo não existir, cria um kernel básico
            kernel.learn("std-startup.xml")
            kernel.respond("load aiml b")
    except Exception as e:
        print(f">> [AVISO AIML] Não foi possível carregar AIML: {e}")

load_aiml()

def speak(text):
    """Usa o eSpeak para falar o texto"""
    try:
        # Limita o texto para evitar comandos muito longos
        if len(text) > 500:
            text = text[:500] + "..."
            
        # Limpa o texto para evitar problemas com aspas no shell
        clean_text = text.replace('"', '\\"').replace("'", "\\'")
        
        # Usa subprocess com lista de argumentos (mais seguro) - SEM TIMEOUT
        subprocess.run([
            'espeak', 
            '-v', 'pt-br', 
            '-s', '150', 
            '-p', '50', 
            '-a', '110',
            clean_text
        ], check=True)  # REMOVIDO: timeout=30
    except subprocess.CalledProcessError as e:
        print(f">> [ERRO TTS] Erro no eSpeak: {e}")
    except FileNotFoundError:
        print(">> [ERRO TTS] eSpeak não encontrado. Instale com: sudo apt-get install espeak")
    except Exception as e:
        print(f">> [ERRO TTS] {e}")

def get_ai_response(prompt):
    """Obtém resposta da API do OpenRouter"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://github.com",
        "X-Title": "Chatbot OpenRouter",
        "Content-Type": "application/json",
    }

    # Prompts mais específicos para melhor resposta em português
    prompt_ptbr = f"Você é um assistente útil. Responda em português brasileiro de forma clara, concisa e natural: {prompt}"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt_ptbr}],
        "temperature": 0.7,
        "max_tokens": 500,  # Reduzido para evitar tokens excessivos
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "Desculpe, não obtive uma resposta válida da API."
            
    except requests.exceptions.HTTPError as err:
        error_msg = f"Erro HTTP {err.response.status_code}"
        try:
            error_detail = err.response.json().get('error', {}).get('message', str(err))
            return f"{error_msg}: {error_detail}"
        except:
            return f"{error_msg}: {err.response.text}"
    except requests.exceptions.Timeout:
        return "Erro: Timeout na conexão com a API."
    except requests.exceptions.ConnectionError:
        return "Erro: Sem conexão com a internet."
    except Exception as e:
        return f"Erro desconhecido: {str(e)}"

def get_news(query):
    """Busca notícias no Google News"""
    try:
        string_formatada = urllib.parse.quote(query, encoding='utf-8')
        news_url = f"https://news.google.com/rss/search?q={string_formatada}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

        req = Request(news_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as Client:
            xml_page = Client.read()

        soup_page = BeautifulSoup(xml_page, "xml")  # Usar "xml" em vez de "lxml-xml"
        news_list = soup_page.findAll("item")
        
        results = []
        for news in news_list[:3]:  # Limita a 3 notícias
            title = news.title.text
            # Remove o nome do site se existir
            if ' - ' in title:
                title = title.split(' - ')[0]
            results.append(title)
        
        return results if results else ["Nenhuma notícia encontrada sobre este assunto."]
    except Exception as e:
        print(f">> [ERRO NEWS] {e}")
        return [f"Erro ao buscar notícias: {str(e)}"]

def get_world_news():
    """Busca as principais notícias mundiais"""
    try:
        req = Request(WORLD_NEWS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as Client:
            xml_page = Client.read()

        soup_page = BeautifulSoup(xml_page, "xml")
        news_list = soup_page.findAll("item")
        
        results = []
        for news in news_list[:5]:  # Corrigido: era 10 no comentário, 5 no código
            title = news.title.text
            if ' - ' in title:
                title = title.split(' - ')[0]
            results.append(title)
        
        return results if results else ["Nenhuma notícia mundial encontrada."]
    except Exception as e:
        print(f">> [ERRO NOTÍCIAS MUNDIAIS] {e}")
        return [f"Erro ao buscar notícias mundiais: {str(e)}"]

def listen_for_speech():
    """Ouve e reconhece fala usando o microfone"""
    r = sr.Recognizer()
    r.energy_threshold = 300  # Threshold fixo para melhor detecção
    r.pause_threshold = 0.8
    
    try:
        with sr.Microphone() as mic:
            print("\nAjustando para ruído ambiente...")
            r.adjust_for_ambient_noise(mic, duration=1)
            
            #playsound('wav/voice_start.wav')
            print("Ouvindo... (fale agora)")
            audio = r.listen(mic, timeout=10, phrase_time_limit=10)

            playsound('/etc/luna/wav/voice_stop.wav')

            print("Reconhecendo...")
            texto = r.recognize_google(audio, language="pt-BR")
            
            print(f"Você disse: {texto}")
            return texto.lower().strip()
            
    except sr.WaitTimeoutError:
        print("Tempo limite atingido. Nada foi detectado.")
        return None
    except sr.UnknownValueError:
        print("Não foi possível entender o áudio.")
        return None
    except sr.RequestError as e:
        print(f"Erro no serviço de reconhecimento: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado no microfone: {e}")
        return None

def process_command(user_input):
    """Processa o comando do usuário"""
    if not user_input:
        return None
        
    user_input = user_input.lower().strip()
    
    # Comandos de saída
    if user_input in ["sair", "exit", "encerrar", "fechar", "parar"]:
        speak("Até logo! Encerrando sistema.")
        playsound('/etc/luna/wav/codec_close.mp3')
        print(">> Sistema encerrado.")
        return "exit"
        
    # Comando de IA
    if user_input.startswith("/ai "):
        prompt = user_input[4:].strip()
        if prompt:
            print(f"[AI] Processando: {prompt}")
            response = get_ai_response(prompt)
            print(f"[AI] Resposta: {response}")
            speak(response)
        else:
            speak("Por favor, forneça uma pergunta após o comando /ai.")
    
    # Comando de notícias específicas
    elif user_input.startswith("news "):
        query = user_input[5:].strip()
        if query:
            print(f"[BUSCANDO] Notícias sobre: {query}")
            news_results = get_news(query)
            for i, news in enumerate(news_results, 1):
                print(f"{i}. {news}")
                speak(news)
                time.sleep(1)
        else:
            speak("Por favor, diga sobre o que quer buscar notícias.")
    
    # Notícias mundiais
    elif user_input in ["mundo", "notícias mundo", "noticias mundo"]:
        print("[NOTÍCIAS MUNDIAIS]")
        world_news = get_world_news()
        for i, news in enumerate(world_news, 1):
            print(f"{i}. {news}")
            speak(f"Notícia {i}: {news}")
            time.sleep(1.5)
    
    # Limpar tela
    elif user_input in ["clear", "cls", "limpar"]:
        os.system("clear" if os.name == 'posix' else 'cls')
        print("=== Luna I.A Assistente por Voz ===")
        print("Comandos: /ai [pergunta], news [tópico], mundo, limpar, sair")
    
    # Comando padrão - tenta AIML primeiro, depois IA
    else:
        try:
            bot_response = kernel.respond(user_input)
            if bot_response and not bot_response.lower().startswith("i don't know") and not bot_response.lower().startswith("warning:"):
                print(f"[AIML] {bot_response}")
                speak(bot_response)
            else:
                # Fallback para IA
                response = get_ai_response(user_input)
                print(f"[AI] {response}")
                speak(response)
        except Exception as e:
            print(f"[ERRO AIML] {e}")
            response = get_ai_response(user_input)
            print(f"[AI] {response}")
            speak(response)
    
    return None

def main():

    playsound('/etc/luna/wav/codec_open.mp3')
    # Verifica dependências
    try:
        subprocess.run(['espeak', '--version'], capture_output=True, check=True)
    except:
        print("AVISO: eSpeak não está instalado. Instale com: sudo apt-get install espeak")
    
    os.system("clear")
    print("=== Luna I.A Assistente por Voz ===")
    print("Comandos disponíveis:")
    print("- /ai [sua pergunta] - Consulta à IA")
    print("- news [tópico] - Notícias sobre um assunto") 
    print("- mundo - Principais notícias mundiais")
    print("- limpar - Limpa a tela")
    print("- sair - Encerra o programa")
    print("\nAguardando comando de voz...")
    
    while True:
        try:
            user_input = listen_for_speech()
            
            if user_input:
                result = process_command(user_input)
                if result == "exit":
                    break
                
            time.sleep(1)  # Pequena pausa entre comandos
            
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário. Encerrando...")
            speak("Encerrando por comando do usuário.")
            playsound('/etc/luna/wav/codec_close.mp3')
            break
        except Exception as e:
            print(f"Erro crítico: {e}")
            speak("Erro crítico no sistema. Reinicie o programa.")
            break

if __name__ == "__main__":
    main()
import requests
import json
import os
import subprocess
import urllib.parse
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen, Request
import aiml
import warnings
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Suprimir warnings de depreciação
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configurações
TELEGRAM_TOKEN = "8403906213:AAFTVm941LHDaIdW2tJ96OZSxaWeQ21PEmM"
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"
WORLD_NEWS_URL = "https://news.google.com/rss/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JYQjBMVUpTR2dKQ1VpZ0FQAQ?hl=pt-BR&gl=BR&ceid=BR%3Apt-419"

# Configurações do grupo específico
TARGET_GROUP = "SobreviventeUrbano"  # Nome do grupo (apenas para referência)
TARGET_CHAT_ID = -1001234567890  # ID real do grupo (obter com /getid no grupo)
TARGET_THREAD_ID = 4031  # ID do tópico "Bate Papo" (obter com /getid no tópico)

# Inicialização do kernel AIML
kernel = aiml.Kernel()
kernel.verbose(False)

# Tentar carregar AIML (com tratamento para erro de time.clock)
try:
    # Patch para resolver problema do time.clock no AIML
    import time
    if not hasattr(time, 'clock'):
        time.clock = time.time
    kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
    logger.info("AIML carregado com sucesso")
except Exception as e:
    logger.warning(f"Erro ao carregar AIML: {e}")

def speak(text):
    """Usa o TTS do Termux para falar o texto"""
    try:
        clean_text = text.replace('"', '\\"').replace("'", "\\'")
        subprocess.run(['termux-tts-speak', clean_text], check=True)
    except Exception as e:
        logger.error(f"Erro TTS: {str(e)}")

def get_ai_response(prompt):
    """Obtém resposta da API do OpenRouter"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://github.com/seu-usuario/seu-projeto",
        "X-Title": "Chatbot OpenRouter",
        "Content-Type": "application/json",
    }

    prompt_ptbr = f"Responda em português brasileiro de forma clara e concisa: {prompt}"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt_ptbr}],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Erro API OpenRouter: {str(e)}")
        return "Desculpe, estou com problemas para acessar minha inteligência artificial no momento."

def get_news(query):
    """Busca notícias no Google News"""
    string_formatada = urllib.parse.quote(query, encoding='utf-8')
    news_url = "https://news.google.com/rss/search?q=" + \
        string_formatada + "&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    try:
        req = Request(news_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as Client:
            xml_page = Client.read()

        soup_page = soup(xml_page, "lxml-xml")
        news_list = soup_page.findAll("item")
        
        results = []
        for news in news_list[:3]:
            title = news.title.text.split(' - ')[0]
            results.append(title)
        
        return results if results else ["Nenhuma notícia encontrada sobre este assunto."]
    except Exception as e:
        logger.error(f"Erro ao buscar notícias: {str(e)}")
        return ["Erro ao buscar notícias. Tente novamente mais tarde."]

def get_world_news():
    """Busca as principais notícias mundiais"""
    try:
        req = Request(WORLD_NEWS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as Client:
            xml_page = Client.read()

        soup_page = soup(xml_page, "lxml-xml")
        news_list = soup_page.findAll("item")
        
        results = []
        for news in news_list[:5]:
            title = news.title.text.split(' - ')[0]
            results.append(title)
        
        return results if results else ["Nenhuma notícia mundial encontrada no momento."]
    except Exception as e:
        logger.error(f"Erro ao buscar notícias mundiais: {str(e)}")
        return ["Erro ao buscar notícias mundiais. Tente novamente mais tarde."]

async def send_to_target_group(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Envia mensagem para o grupo e tópico específico"""
    try:
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            message_thread_id=TARGET_THREAD_ID,
            text=message
        )
        logger.info(f"Mensagem enviada para o grupo {TARGET_GROUP}, tópico {TARGET_THREAD_ID}")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem para o grupo: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    keyboard = [
        [InlineKeyboardButton("Notícias Mundo", callback_data="mundo")],
        [InlineKeyboardButton("Ajuda", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "Olá! Sou a Luna I.A, seu assistente inteligente.\n\n"
        "Sistemas disponíveis:\n"
        "• AIML - respostas pré-programadas\n"
        "• Mistral-7B - IA generativa\n"
        "• Notícias (use /news assunto)\n"
        "• Notícias Mundiais (use /mundo)\n\n"
        "Digite sua mensagem ou use os comandos abaixo:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = (
        "Comandos disponíveis:\n\n"
        "/start - Iniciar o bot\n"
        "/help - Mostrar esta ajuda\n"
        "/news assunto - Buscar notícias sobre um assunto\n"
        "/mundo - Principais notícias mundiais\n"
        "/ai pergunta - Usar apenas a IA generativa\n"
        "/getid - Obter IDs do chat e tópico\n\n"
        "Ou simplesmente digite sua mensagem para conversar normalmente!"
    )
    await update.message.reply_text(help_text)

async def getid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /getid - Para obter IDs do chat e tópico"""
    chat_id = update.message.chat_id
    message_thread_id = update.message.message_thread_id
    
    response = (
        f"Chat ID: {chat_id}\n"
        f"Thread ID: {message_thread_id}\n"
        f"Chat Type: {update.message.chat.type}\n\n"
        "Use esses IDs na configuração do bot."
    )
    
    await update.message.reply_text(response)

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /news"""
    if not context.args:
        await update.message.reply_text("Por favor, digite o assunto das notícias. Exemplo: /news tecnologia")
        return
    
    query = " ".join(context.args)
    await update.message.reply_text(f"Buscando notícias sobre '{query}'...")
    
    news_results = get_news(query)
    response_text = f"Notícias sobre '{query}':\n\n"
    
    for i, news in enumerate(news_results, 1):
        response_text += f"{i}. {news}\n\n"
    
    await update.message.reply_text(response_text)
    
    # Enviar também para o grupo alvo
    await send_to_target_group(context, response_text)

async def mundo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /mundo"""
    await update.message.reply_text("Buscando principais notícias mundiais...")
    
    world_news = get_world_news()
    response_text = "Principais notícias mundiais:\n\n"
    
    for i, news in enumerate(world_news, 1):
        response_text += f"{i}. {news}\n\n"
    
    await update.message.reply_text(response_text)
    
    # Enviar também para o grupo alvo
    await send_to_target_group(context, response_text)

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ai"""
    if not context.args:
        await update.message.reply_text("Por favor, digite sua pergunta. Exemplo: /ai explique a teoria da relatividade")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text("Processando sua pergunta com a IA...")
    
    response = get_ai_response(prompt)
    await update.message.reply_text(f"IA Responde:\n\n{response}")
    
    # Enviar também para o grupo alvo se for uma pergunta relevante
    if len(prompt) > 10:  # Só envia perguntas mais substanciais
        await send_to_target_group(context, f"Pergunta: {prompt}\n\nResposta: {response}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com mensagens normais"""
    user_input = update.message.text.strip()
    
    if not user_input:
        await update.message.reply_text("Por favor, digite algo.")
        return
    
    # Primeiro tenta AIML
    try:
        bot_response = kernel.respond(user_input)
    except:
        bot_response = None
    
    if not bot_response or bot_response.lower().startswith("warning:"):
        # Se AIML não souber, usa a IA
        await update.message.reply_text("Processando sua mensagem...")
        response = get_ai_response(user_input)
        await update.message.reply_text(f"IA Responde:\n\n{response}")
        
        # Enviar também para o grupo alvo se for uma mensagem relevante
        if len(user_input) > 10 and not user_input.startswith('/'):
            await send_to_target_group(context, f"Mensagem: {user_input}\n\nResposta: {response}")
    else:
        await update.message.reply_text(f"Resposta:\n\n{bot_response}")
        
        # Enviar também para o grupo alvo
        await send_to_target_group(context, f"Mensagem: {user_input}\n\nResposta: {bot_response}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com cliques nos botões"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "mundo":
        await query.edit_message_text("Buscando principais notícias mundiais...")
        world_news = get_world_news()
        response_text = "Principais notícias mundiais:\n\n"
        for i, news in enumerate(world_news, 1):
            response_text += f"{i}. {news}\n\n"
        await query.edit_message_text(response_text)
        
        # Enviar também para o grupo alvo
        await send_to_target_group(context, response_text)
        
    elif query.data == "help":
        help_text = (
            "Comandos disponíveis:\n\n"
            "/start - Iniciar o bot\n"
            "/help - Mostrar esta ajuda\n"
            "/news assunto - Buscar notícias sobre um assunto\n"
            "/mundo - Principais notícias mundiais\n"
            "/ai pergunta - Usar apenas a IA generativa\n"
            "/getid - Obter IDs do chat e tópico\n\n"
            "Ou simplesmente digite sua mensagem para conversar normalmente!"
        )
        await query.edit_message_text(help_text)

def main():
    """Função principal"""
    print("Iniciando Luna I.A Telegram Bot...")
    print(f"Grupo alvo: {TARGET_GROUP}")
    print(f"Chat ID: {TARGET_CHAT_ID}")
    print(f"Thread ID: {TARGET_THREAD_ID}")
    
    # Criar aplicação
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("getid", getid_command))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("mundo", mundo_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar o bot
    print("Bot iniciado. Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()

import os 
import base64
import telebot 

from groq import Groq
from dotenv import load_dotenv

load_dotenv

TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')

print("Token cargado:", TOKEN_BOT_TELEGRAM)

CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')
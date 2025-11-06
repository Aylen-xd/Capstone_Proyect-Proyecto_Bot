import os 
import base64
import telebot 

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("⚠️ Faltan claves en el archivo .env. Verifica TELEGRAM_BOT_TOKEN y GROQ_API_KEY.")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    bot.reply_to(message, "👋 ¡Hola! Envíame una imagen y te ayudare con lo que necesites")

@bot.message_handler(content_types=['photo'])
def procesar_imagen(message):
    try:
        bot.reply_to(message, "🔍 Procesando la imagen, por favor espera un momento...")

        # Descargar la imagen de Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Convertir la imagen a Base64
        img_b64 = base64.b64encode(downloaded_file).decode('utf-8')

        # Enviar la imagen al modelo de Groq (LLaMA 3.2 Vision)
        response = groq_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Describe detalladamente esta imagen en español."
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{img_b64}"
                        }
                    ]
                }
            ]
        )

        descripcion = response.choices[0].message.content
        bot.reply_to(message, f"Esto es lo que veo:\n\n{descripcion}")

    except Exception as e:
        bot.reply_to(message, f"Hubo un error al procesar la imagen: {e}")
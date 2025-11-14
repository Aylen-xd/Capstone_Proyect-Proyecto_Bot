import os
import base64
import json
import telebot

from groq import Groq
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ = os.getenv("GROQ_API_KEY")

# Validar que existan las claves
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno.")
if not GROQ:
    raise ValueError("GROQ_API_KEY no está configurado en las variables de entorno.")

# Inicializar el bot de Telegram y el cliente de Groq
bot = telebot.TeleBot(TOKEN)
cliente_groq = Groq(api_key=GROQ)


# --- Función para convertir imagen a Base64 ---
def imagen_a_base64(ruta_o_bytes_imagen):
    """Convierte una imagen a base64 para enviarla a Groq."""
    try:
        if isinstance(ruta_o_bytes_imagen, bytes):
            # Si ya viene en bytes (como desde Telegram)
            return base64.b64encode(ruta_o_bytes_imagen).decode('utf-8')
        else:
            # Si se pasa una ruta de archivo
            with open(ruta_o_bytes_imagen, "rb") as archivo_imagen:
                return base64.b64encode(archivo_imagen.read()).decode('utf-8')
    except Exception as e:
        print(f"⚠️ Error al convertir imagen a base64: {e}")
        return None


# --- Función para pedirle a Groq que describa la imagen ---
def describir_imagen_con_groq(imagen_base64):
    """Envía la imagen a Groq y obtiene una descripción."""
    try:
        completado_chat = cliente_groq.chat.completions.create(
            model="llama-3.2-11b-vision-preview",  # modelo visual de Groq
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Describe esta imagen de forma detallada en español. "
                                "Menciona los objetos, personas, colores, entorno y cualquier detalle relevante."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{imagen_base64}"
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return completado_chat.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Error al describir imagen con Groq: {e}")
        return None


# --- Comando /start ---
@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    bot.reply_to(message, "👋 ¡Hola! Envíame una imagen y te diré lo que veo.")


# --- Procesar imagen enviada ---
@bot.message_handler(content_types=['photo'])
def procesar_imagen(message):
    try:
        bot.reply_to(message, "📸 Imagen recibida, analizando...")

        # Descargar la imagen desde Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Convertir imagen a Base64
        imagen_b64 = imagen_a_base64(downloaded_file)

        if not imagen_b64:
            bot.reply_to(message, "❌ No pude convertir la imagen, intenta de nuevo.")
            return

        # Pedir descripción a Groq
        descripcion = describir_imagen_con_groq(imagen_b64)

        if descripcion:
            bot.reply_to(message, f"🖼️ *Descripción de la imagen:*\n\n{descripcion}", parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ No pude obtener una descripción de la imagen.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error al procesar la imagen: {e}")


# --- Mensajes que no son imágenes ---
@bot.message_handler(func=lambda message: True)
def manejar_texto(message):
    bot.reply_to(message, "💬 Envíame una *imagen* para analizarla. Usa /start si querés comenzar de nuevo.")


# --- Iniciar el bot ---
if __name__ == "__main__":
    print("🤖 Bot iniciado y escuchando mensajes...")
    bot.polling(none_stop=True)

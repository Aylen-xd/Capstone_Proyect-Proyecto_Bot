"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Carga del token desde .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Soy tu bot de prueba. Envíame un audio y te lo convierto a texto.")

# Mensajes de audio (más adelante integrarás tu feature de voz acá)
async def manejar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Recibí tu audio (todavía no lo proceso).")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Agregar comandos y handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, manejar_audio))

    print("🤖 Bot en ejecución... (Ctrl+C para detener)")
    app.run_polling()

if __name__ == "__main__":
    main()

    
"""

import os
import speech_recognition as sr
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ContextTypes

def convertir_audio_a_texto(ruta_audio):
    recognizer = sr.Recognizer()
    with sr.AudioFile(ruta_audio) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data, language="es-ES")
    except sr.UnknownValueError:
        return "No se pudo entender el audio."
    except sr.RequestError:
        return "Error al conectarse con el servicio de reconocimiento."

async def manejar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Descargar audio desde Telegram
    archivo = await update.message.voice.get_file()
    ruta_ogg = "mensaje.ogg"
    ruta_wav = "mensaje.wav"
    await archivo.download_to_drive(ruta_ogg)

    # Convertir OGG → WAV
    AudioSegment.from_file(ruta_ogg).export(ruta_wav, format="wav")

    # Convertir a texto
    texto = convertir_audio_a_texto(ruta_wav)

    # Responder en Telegram
    await update.message.reply_text(f"📝 Transcripción:\n\n{texto}")

    # Limpiar archivos temporales
    os.remove(ruta_ogg)
    os.remove(ruta_wav)
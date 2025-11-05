import telebot as tlb
import os 
import json
from groq import Groq
from typing import Optional
import time 
from dotenv import load_dotenv

import speech_recognition as sr

#cargar variables del entorno
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def convertir_audio_a_texto(ruta_audio):
    """Convierte un archivo de audio a texto usando SpeechRecognition."""
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(ruta_audio) as source:
        audio = recognizer.record(source)
    
    try:
        texto = recognizer.recognize_google(audio, language="es-ES")
        return texto
    except sr.UnknownValueError:
        return "No se pudo entender el audio."
    except sr.RequestError:
        return "Error al conectarse con el servicio de reconocimiento."

if __name__ == "__main__":
    # Ejemplo de prueba local (reemplazá 'audio.wav' con un archivo real)
    ruta = "audio.wav"
    if os.path.exists(ruta):
        resultado = convertir_audio_a_texto(ruta)
        print("Texto reconocido:", resultado)
    else:
        print("No se encontró el archivo de audio.")




        # /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Soy tu bot de prueba. Envíame un audio y te lo convierto a texto.")

# Mensajes de audio (más adelante integrarás tu feature de voz acá)
async def manejar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Recibí tu audio (todavía no lo proceso).")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Agregar comandos y handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, manejar_audio))

    print("🤖 Bot en ejecución... (Ctrl+C para detener)")
    app.run_polling()

if __name__ == "__main__":
    main()
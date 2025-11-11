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
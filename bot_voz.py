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
print("TOKEN ENCONTRADO:", TOKEN)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROK_TELEGRAM')


#Validacion de carga de variable
if not TELEGRAM_TOKEN:
    #print(f"Tu variable de entorno de telegram no ta: {}")
    raise ValueError("El token de telegram se cargo")
if not GROQ_API_KEY:
    raise ValueError("No se encuentra API_KEY de Groq")

#Instanciar objetos de clase
bot = tlb.TeleBot(TELEGRAM_TOKEN)
grok_client = Groq(api_key=GROQ_API_KEY)

def load_company_data():
    try:
        with open("DataSuper.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar el json: {str(e)}")
        return None
    
company_data = load_company_data()

def get_groq_response(user_message: str):
    try:
        system_prompt = f""" Eres es asistente virtual de un Supermercadp. Tu tarea s responder preguntas basandote UNICAMENTE en la siguiente informacion de la empresa. Si te pregunta algo que no está en estos datos, indica amablemente que no puedes proporcionar esa ifnormacion y sugiere contactar directamente con la empresa. 

    Datos de la empresa:
    {json.dump(company_data, ensure_ascii=False,indent=2)}

    Reglas importantes:
    1- Solo responder con la infromacion que este en el dataset proporcionado
    2- No inventes ni añadas informacion adicional.
    3- Si l ainfromacion solicitada no se encuentra en el dataset, sugiere contactar a supermercado.com
    4- No responder preguntas no relacionadas con la empresa
    """
        
        chat_completion = groq_client.chat.completions.create(
            message = [
                {
                    "role": "system"
                }
            ]
        )


    except 


"""
def convertir_audio_a_texto(ruta_audio):
    
    """#Convierte un archivo de audio a texto usando SpeechRecognition."""
"""
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

"""
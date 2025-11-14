#Este chat bot va a ocntestar a partir del dataset, la IA saca la informacion directo del dataset

import telebot as tlb #este si
import os #este si
import json #este si
from groq import Groq #este s
from typing import Optional #este si
import time #este si
from dotenv import load_dotenv #este si

import speech_recognition as sr

print("--- Script Iniciado con éxito ---")

#cargar variables del entorno
load_dotenv()
#print("TOKEN ENCONTRADO:", TOKEN)

#levanta las variables de entorno
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

#verificar que todo funcione
#Validacion de carga de variable
if not TELEGRAM_TOKEN:
    #print(f"Tu variable de entorno de telegram no ta: {}")
    raise ValueError("El token de telegram se cargo")
if not GROQ_API_KEY:
    raise ValueError("No se encuentra API_KEY de Groq")


#crear objetos del tipo de la clase
#Instanciar objetos de clase
bot = tlb.TeleBot(TELEGRAM_TOKEN) #se pasa la contstante, que trae la variable de la otra clase
grok_client = Groq(api_key=GROQ_API_KEY)


#necesito instalar un json, recorrerlo y leerlo (abrir, leer y cargarlo)
def load_company_data():
    try:
        #abrir json: donde esat el archivo, codificarlo para que lo lea bien.
        with open("DataSuper.json", "r", encoding="utf-8") as f:
            return json.load(f)
        
        #en el caso que no lo cargo sin romper el programa. 
        #cualquier error que exista, que pase esto.
    except Exception as e:
        print(f"Error al cargar el json: {str(e)}")
        return None


#asignamos a company_data el load en una funcion, para necesito cargarlo en otro momento.
company_data = load_company_data()


#funcion, que pide de parametro un user_message
def get_groq_response(user_message: str):
    try:
        #funciones de funcionamiento  -   #dataset para jason es un diccionario
        system_prompt = f""" Eres es asistente virtual de un Supermercadp. Tu tarea es responder preguntas basandote UNICAMENTE en la siguiente informacion de la empresa. Si te pregunta algo que no está en estos datos, indica amablemente que no puedes proporcionar esa informacion y sugiere contactar directamente con la empresa. 

    Datos de la empresa:
    {json.dumps(company_data, ensure_ascii=False,indent=2)}

    Reglas importantes:
    1- Solo responder con la infromacion que este en el dataset proporcionado
    2- No inventes ni añadas informacion adicional.
    3- Si l ainfromacion solicitada no se encuentra en el dataset, sugiere contactar a supermercado.com
    4- No responder preguntas no relacionadas con la empresa
    """
        chat_completion = grok_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500
        )

        return chat_completion.choices[0].message.content.strip()

    
    except Exception as e:
        print(f"No se puedo obtener la reuesta: {str(e)}")
        return None
 
"""
def transcribe_voic_with_groq(message: tlb.types.Message) -> Optional[str]:
    try: 
        file_info = bot.get_file(message.voice.file_id)
        download_file = bot.download_file(file_info.file_path)
        temp_file = "temp_voice.ogg"

        #guardar el archivo de forma temporal
        with open(temp_file, "wb") as f:
            f.write(download_file)
        with open(temp_file, "rb") as file:
            transcription = grok_client.audio.transcriptions.create(
                file = (temp_file, file.read()),
                model = "whisper-large-v3-turbo",
                prompt = "especificar contexto o pronunciacion",
                response_format="json",  
                language="es",   
                temperature=1
            )

            os.remove(temp_file)

            return transcription.text
        
    except Exception as e:
        print(f"Error al transcribir: {str(e)}")
        return None
"""
def transcribe_voic_with_groq(message: tlb.types.Message) -> Optional[str]:
    temp_file = "temp_voice.ogg"

    try:
        # Descarga de Telegram
        file_info = bot.get_file(message.voice.file_id)
        download_file = bot.download_file(file_info.file_path)

        # Guardar archivo temporal
        with open(temp_file, "wb") as f:
            f.write(download_file)

        # Leer archivo COMPLETO en memoria
        with open(temp_file, "rb") as f:
            audio_bytes = f.read()

        # Enviar a Groq
        transcription = grok_client.audio.transcriptions.create(
            file=("temp_voice.ogg", audio_bytes),
            model="whisper-large-v3-turbo",
            prompt="Transcribe el audio en español.",
            response_format="json",
            language="es",
            temperature=0
        )

        return transcription.text

    except Exception as e:
        print(f"Error al transcribir: {str(e)}")
        return None

    finally:
        # Borrar archivo temporal si existe
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass


#PROGRAMAR LO QUE EL BOT VA A HACER


#comando que va a usar el bot
@bot.message_handler(commands=["start", "help"])

def send_welcome(message: tlb.types.Message):
    if not company_data:
        bot.reply_to(message, "Error no se cargaron los datos de la empresa, porfa intente mas tarde")
        return 
    bot.send_chat_action(message.chat.id, "Typing")

    welcome_prompt = "generar un mensaje de bienvenida para el SupermercadoIA, que incluya una breve descripcion del bot y que mencione que puede consultar de productos y precios en base a los audios que envian"

    response = get_groq_response(message.text)

    if response:
        bot.reply_to(message, response)
    else:
        error = "perdon, no pude procesar su mensaje, vuelva despues"
        bot.reply_to(message, error)

#restos de mensajes
#manipulacion de texto
@bot.message_handler(content_types=['text'])
def handle_text_message(message: tlb.types.Message):
    if not company_data:
        bot.reply_to(message, "Error no se cargaron los datos de la empresa, por favor intente mas tarde")
        return 
    bot.send_chat_action(message.chat.id, "typing")
    response = get_groq_response(message.text)

    if response:
        bot.reply_to(message, response)
    else:
        error = "perdon, no pude procesar su mensaje de voz, vuelva despues"
        bot.reply_to(message, error)

#HASTA ACA FUE PARTE DE TEXTO

#MANEJAR VOZ
@bot.message_handler(content_types=['voice'])
def hanlder_voice_message(message: tlb.types.Message):
    if not company_data:
        bot.reply_to(message, "Error al cargar los datos de la empresa. Por favor, intente mas tarde.")
        return
    bot.send_chat_action(message.chat.id, "Typing")

    #llamo la funcion de transcribe voice with groq y le tengo que mandar un mensaje

    transcription = transcribe_voic_with_groq(message)

    if not transcription:
        bot.reply_to(message, "Perdon no puedo transcribir tu audio, saludos")
        return
    #si lo transcribe le mandamos a goq para que haga su respuesta
    response = get_groq_response(transcription)
    if response:
        bot.reply_to(message, response)
    else: error = "No pude procesar la consulta"


if __name__ == "__main__":
    if company_data:
        print(f"Bot de {company_data['company_info']['name']} iniciado correctamente")

        while True:
            try:
                bot.polling(none_stop= True, interval=0, timeout=25)
            except Exception as e:
                print(f"Error, no se pudo procesar por: {str(e)}")
                print("Reiniciando el bot")
                time.sleep(5)
            else: print(f"No se pudo cargar nada, fijate donde esta el error bobi")

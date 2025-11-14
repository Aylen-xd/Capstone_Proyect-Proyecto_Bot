import os
import base64
import telebot

from groq import Groq
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROQ = os.getenv('GROQ_API_KEY')

#verificar
print(TOKEN) 
print(GROQ)
print("TOKEN ->", repr(TOKEN))


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
        print(f"Error al convertir imagen a base64!: {e}")
        return None


# --- Función para pedirle a Groq que describa la imagen ---
def describir_imagen_con_groq(imagen_base64):
    """Envía la imagen a Groq y obtiene una descripción."""
    
    try:
        completado_chat = cliente_groq.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe esta imagen de forma detallada en español. Menciona los objetos, personas, colores, entorno y cualquier detalle relevante."
                        },
                        {
                            "type": "image_url",
                            "image_url":{
                                "url": f"data:image/jpeg;base64,{imagen_base64}"
                            }
                        }
                    ]
                }
            ],
            moder= "meta-llama/llama-4-scout-17b-16e-instruct",

            temperature=0.7,
            max_tokens=2000
        )
        return completado_chat.choices[0].message.content
    
    except Exception as e:
        print(f"⚠️ Error al describir imagen con Groq: {e}")
        return None


# --- Comando /start ---
@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    """Mensaje de bienvenida"""

    texto_bienvenida = """
¡Hola! 👋 Soy un bot que puede describir imágenes para ti.


🖼️ **¿Cómo funciono?**
Simplemente envíame una imagen y yo te daré una descripción detallada de lo que veo.


🤖 **Tecnología:**
Utilizo Groq AI para analizar las imágenes y generar descripciones precisas.


📸 **¡Pruébame!**
Envía cualquier imagen y verás lo que puedo hacer.


Para obtener ayuda, usa el comando /help
    # Cierra el string multi-línea y termina la asignación a texto_bienvenida
"""
    bot.reply_to(message, texto_bienvenida)

bot.message_handler(commands=['help'])


# Define la función que manejará el comando /help
def enviar_ayuda(mensaje):

    """Mensaje de ayuda"""
   
    # Contiene toda la información de ayuda para el usuario
    texto_ayuda = """
🔧 **Comandos disponibles:**


/start - Iniciar el bot
/help - Mostrar esta ayuda


📸 **¿Cómo usar el bot?**


1. Envía una imagen (foto, dibujo, captura, etc.)
2. Espera unos segundos mientras proceso la imagen
3. Recibirás una descripción detallada de lo que veo


💡 **Consejos:**
- Las imágenes más claras y nítidas generan mejores descripciones
- Puedo analizar fotos, dibujos, gráficos, capturas de pantalla, etc.
- Respondo en español siempre


❓ **¿Problemas?**
Si algo no funciona, intenta enviar la imagen de nuevo.
    # Cierra el string multi-línea
    """
    
    bot.reply_to(mensaje, texto_ayuda)




# --- Procesar imagen enviada ---
@bot.message_handler(content_types=['photo'])
def procesar_imagen(message):
    """Procesa las imagenes envidadas por el usuario"""

    try:
        bot.reply_to(message, "📸 Imagen recibida, analizando...")

        # Descargar la imagen desde Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        archivo_descargado = bot.download_file(file_info.file_path)

        # Convertir imagen a Base64
        imagen_b64 = imagen_a_base64(archivo_descargado)

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

        print(f"error al procesar la imagen: {e}")
        bot.reply_to(message, f"❌ Ocurrió un error al procesar tu imagen. Intenta de nuevo.")


# --- Mensajes que no son imágenes ---
@bot.message_handler(func=lambda message: True)
def manejar_texto(message):
    """Maneja mensajes que no son comandos ni imagenes"""
    bot.reply_to(message, "💬 Envíame una *imagen* para analizarla. Usa /start si querés comenzar de nuevo.")


# --- Iniciar el bot ---
if __name__ == "__main__":
    print("🤖 Bot iniciado y escuchando mensajes...")
    print("📸 Esperando imágenes para describir...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        # Esto ayuda a diagnosticar por qué el bot no pudo iniciar
        print(f"Error al iniciar el bot: {e}")


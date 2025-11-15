import telebot          # Librería para el bot de Telegram
import os               # Manejo de archivos
import json             # Para leer dataset.json
import requests         # Para llamar a la API de Groq

# ============================================================
# 🔧 1. CONFIGURACIÓN (Solo reemplaza tu API key real de Groq)
# ============================================================

TELEGRAM_TOKEN = "8277619261:AAFXPLlyPgX-wTvWidlKQAR8spp-VmAsEEE"

GROQ_API_KEY = "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"  # ⚠️ Reemplazar por tu clave real

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

DATASET_PATH = "dataset.json"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ============================================================
# 📚 2. FUNCIONES DE DATOS Y LÓGICA
# ============================================================

# Cargar datos del supermercado desde JSON
def cargar_dataset():
    try:
        if os.path.exists(DATASET_PATH):
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"[⚠️ Error al cargar dataset: {e}]")
        return []


dataset = cargar_dataset()


# Buscar respuestas fijas o relacionadas con el supermercado
def buscar_en_dataset(pregunta, dataset):
    pregunta_lower = pregunta.lower()

    if "oferta" in pregunta_lower or "descuento" in pregunta_lower:
        return "🛍️ ¡Hoy tenemos *20% de descuento* en frutas y verduras 🍎🥦 y *3x2 en lácteos*! 🧀"
    elif "horario" in pregunta_lower or "abierto" in pregunta_lower:
        return "🕐 Nuestro horario es de *lunes a sábado de 8 a 21 hs*, y los *domingos de 9 a 14 hs*."
    elif "ubicación" in pregunta_lower or "dónde está" in pregunta_lower:
        return "📍 La sección de lácteos está en el *pasillo 5*, y las carnes en la *última nevera* 🥩."
    elif "contacto" in pregunta_lower:
        return "📞 Podés llamarnos al *555-1234* para consultas o pedidos."
    elif "receta" in pregunta_lower or "cocinar" in pregunta_lower or "ingredientes" in pregunta_lower:
        return (
            "🍳 ¡Claro! Decime *qué ingrediente tenés* (por ejemplo: pollo, pasta o tomate) "
            "y te sugeriré una receta y su lista de compras 🛒."
        )
    elif "lista" in pregunta_lower:
        return (
            "🧾 Podés usarme como lista de compras. Solo decime 'agregar arroz', 'quitar pan', "
            "o 'mostrar mi lista' y te ayudaré a organizar todo fácilmente."
        )

    return None


# Consultar a Groq para generar respuestas más complejas o recetas
def respuesta_groq(mensaje):
    if GROQ_API_KEY == "TU-GROQ-API-AQUI":
        return "⚠️ No configuraste tu *API Key de Groq*. No puedo generar respuestas avanzadas todavía."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sos Supermercado.AI, un asistente de supermercado amable y útil. "
                    "Ayudás con recetas, precios, productos, y organización de listas. "
                    "Cuando te pidan una receta, respondé con un formato simple: título, ingredientes y pasos breves. "
                    "Usá un tono natural, simpático y claro."
                ),
            },
            {"role": "user", "content": mensaje},
        ],
        "max_tokens": 350,
        "temperature": 0.7,
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=25)

        if response.status_code == 200:
            result = response.json()
            contenido = result["choices"][0]["message"]["content"].strip()
            return contenido
        else:
            return f"😕 Error al conectar con Groq (Código {response.status_code}). Revisá tu API Key."

    except Exception as e:
        return f"⚠️ Error de conexión con Groq: {e}"


# ============================================================
# 💬 3. HANDLERS DE TELEGRAM
# ============================================================

# /start y /help
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bienvenida = (
        "👋 ¡Hola! Soy *Supermercado.AI*, tu asistente personal de compras 🛒\n\n"
        "Puedo ayudarte con:\n"
        "• 🛍️ Ofertas y precios\n"
        "• 🍳 Recetas según tus ingredientes\n"
        "• 📦 Organización de tu lista de compras\n"
        "• 📍 Información de secciones del supermercado\n\n"
        "Escribime lo que necesites o usá /help para ver los comandos disponibles."
    )
    bot.reply_to(message, bienvenida, parse_mode="Markdown")


# Cualquier mensaje de texto
@bot.message_handler(func=lambda message: True)
def responder(message):
    pregunta = message.text.strip()
    print(f"[💬 Mensaje recibido]: {pregunta}")

    # 1️⃣ Intentar una respuesta del dataset o respuestas fijas
    respuesta = buscar_en_dataset(pregunta, dataset)

    # 2️⃣ Si no se encuentra, pedir ayuda a Groq
    if not respuesta:
        respuesta = respuesta_groq(pregunta)

    # 3️⃣ Enviar la respuesta final
    bot.reply_to(message, respuesta, parse_mode="Markdown")


# ============================================================
# 🏁 4. EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    print("🚀 Supermercado.AI iniciado con éxito. Esperando mensajes en Telegram...")
    bot.infinity_polling(skip_pending=True)

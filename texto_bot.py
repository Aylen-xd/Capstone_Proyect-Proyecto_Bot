import telebot
import os
import json
import requests

# ============================================================
# 1. CONFIG
# ============================================================
TELEGRAM_TOKEN = "8277619261:AAFXPLlyPgX-wTvWidlKQAR8spp-VmAsEEE"
GROQ_API_KEY = "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"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DATASET_PATH = "dataset.json"

bot = telebot.TeleBot(TELEGRAM_TOKEN)


# ============================================================
# 2. CARGA DE DATASET
# ============================================================

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


def buscar_en_dataset(pregunta, dataset):
    p = pregunta.lower()

    if "oferta" in p or "descuento" in p:
        return "🛍️ ¡Hoy tenemos *20% de descuento* en frutas y verduras! 🍎🥦"

    if "horario" in p or "abierto" in p:
        return "🕐 Horario: *Lun-Sab 8 a 21 hs*, Dom *9 a 14 hs*."

    if "ubicación" in p:
        return "📍 Lácteos → *pasillo 5* | Carnes → *última heladera* 🥩"

    if "contacto" in p:
        return "📞 Teléfono: *555-1234*"

    if "receta" in p:
        return "🍳 Decime un ingrediente y te sugiero una receta."

    if "lista" in p:
        return "🧾 Puedo organizar tu lista de compras. Probá: *agregar arroz*."

    return None


# ============================================================
# 3. FUNCIÓN GROQ
# ============================================================

def respuesta_groq(mensaje):
    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Sos Supermercado.AI, un asistente simpático que ayuda con recetas, "
                            "precios, productos y listas de compras."
                        )
                    },
                    {"role": "user", "content": mensaje}
                ],
                "max_tokens": 350,
                "temperature": 0.7
            },
            timeout=25
        )

        data = response.json()

        if response.status_code != 200:
            return f"⚠️ Groq devolvió un error {response.status_code}: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠️ Error conectando con Groq: {e}"


# ============================================================
# 4. TELEGRAM HANDLERS
# ============================================================

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message,
        "👋 ¡Hola! Soy *Supermercado.AI*, tu asistente personal de compras 🛒\n"
        "Preguntame sobre ofertas, recetas, listas o productos.",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: True)
def responder(message):
    pregunta = message.text.strip()
    print(f"[💬 Recibido]: {pregunta}")

    respuesta = buscar_en_dataset(pregunta, dataset) or respuesta_groq(pregunta)

    bot.reply_to(message, respuesta, parse_mode="Markdown")


# ============================================================
# 5. BOT START
# ============================================================

if __name__ == "__main__":
    print("🚀 Supermercado.AI corriendo...")
    bot.infinity_polling(skip_pending=True)

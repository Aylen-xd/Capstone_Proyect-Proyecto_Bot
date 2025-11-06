import os 

TOKEN_BOT_TELEGRAM = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN_BOT_TELEGRAM:
    print("Token encontrado")
else:
    print("token no encontrado")
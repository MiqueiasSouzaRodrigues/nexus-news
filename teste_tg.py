from dotenv import load_dotenv
import os
import requests

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": "🤖 Teste de conexão: O Nexus Brief está online!"}

print(f"Tentando enviar para {CHAT_ID}...")
r = requests.post(url, json=data)
print(r.text)
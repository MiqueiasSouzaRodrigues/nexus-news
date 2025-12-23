from dotenv import load_dotenv
from twilio.rest import Client
import os

load_dotenv()

def testar_envio():
    sid = os.getenv("TWILIO_SID")
    token = os.getenv("TWILIO_TOKEN")
    from_ = os.getenv("TWILIO_FROM")
    to_ = os.getenv("TWILIO_TO")

    if not sid or not token:
        print("❌ Erro: Credenciais do .env não encontradas.")
        return

    print(f"📡 Tentando enviar de {from_} para {to_}...")
    client = Client(sid, token)

    try:
        # Teste com uma imagem pública garantida (Logo do Python)
        img_url = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
        
        message = client.messages.create(
            from_=from_,
            to=to_,
            body="🤖 Teste de Imagem: Se você vê isso, o sistema de envio está OK.",
            media_url=[img_url]
        )
        print(f"✅ Sucesso! Mensagem enviada. SID: {message.sid}")
    except Exception as e:
        print(f"❌ Erro no Twilio: {e}")

if __name__ == "__main__":
    testar_envio()
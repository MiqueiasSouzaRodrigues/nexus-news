import requests
import time

# COLE SEU TOKEN AQUI (O QUE O BOTFATHER DEU)
TOKEN = "8366797521:AAFje-O6UGtszjjM7iTBTcSTeLEtNq0xBLA" 

def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data['result']:
            print("⚠️ Nenhuma mensagem encontrada. Mande um 'Oi' no canal onde o bot é admin!")
            return

        for result in data['result']:
            if 'channel_post' in result:
                chat = result['channel_post']['chat']
                print(f"✅ SUCESSO! O ID do Canal '{chat['title']}' é: {chat['id']}")
                print("Copie esse número (incluindo o sinal de menos, se tiver) para o seu .env")
                return
            
        print("Ainda procurando... (Certifique-se que mandou mensagem no CANAL, não no privado)")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    get_updates()
import requests
import os
import time

def send_digest(articles):
    if not articles: return False

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração do Telegram ausente no .env")
        return False

    print(f"📤 Enviando {len(articles)} notícias para o Canal Telegram...")
    sent_count = 0

    for art in articles:
        try:
            # 1. Preparar os dados
            title = art.get('headline_pt', art.get('title'))
            desk = art.get('desk', 'NEWS').upper()
            source = art.get('source', 'Fonte')
            
            # Link da Imagem e do Site (Gerados pelo GitHub Pages)
            image_url = art.get('image_url') 
            article_url = art.get('url') # Link do seu HTML
            
            # 2. Formatar a Legenda (HTML)
            # <b>Negrito</b>, <a href='...'>Link</a>
            caption = f"<b>{desk} | {source}</b>\n\n"
            caption += f"🚀 <b>{title}</b>\n\n"
            caption += f"<i>{art.get('ai_summary', '')}</i>\n\n"
            caption += f"🔗 <a href='{article_url}'>Ler Matéria Completa e Análise</a>"

            # 3. Enviar Foto com Legenda
            # Se tiver imagem (URL do GitHub), manda 'sendPhoto'. Se não, manda 'sendMessage'.
            if image_url and "http" in image_url:
                url_api = f"https://api.telegram.org/bot{token}/sendPhoto"
                payload = {
                    "chat_id": chat_id,
                    "photo": image_url,
                    "caption": caption,
                    "parse_mode": "HTML"
                }
            else:
                url_api = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": caption, # No sendMessage o campo é 'text'
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False
                }

            # Disparo
            r = requests.post(url_api, json=payload)
            
            if r.status_code == 200:
                print(f"   ✅ Enviado: {title[:20]}...")
                sent_count += 1
            else:
                print(f"   ❌ Erro Telegram: {r.text}")
            
            time.sleep(3) # Evitar flood limit

        except Exception as e:
            print(f"   ❌ Falha crítica: {e}")

    return sent_count > 0
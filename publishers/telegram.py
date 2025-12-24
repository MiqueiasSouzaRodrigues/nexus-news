import requests
import os
import time

# Função principal (Notícias Aprovadas)
def send_digest(articles):
    if not articles: return False

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração do Telegram ausente.")
        return False

    print(f"📤 Enviando {len(articles)} notícias para o Telegram...")
    sent_count = 0

    for art in articles:
        try:
            # Dados Básicos
            title = art.get('headline_pt', art.get('title'))
            desk = art.get('desk', 'NEWS').upper()
            source = art.get('source', 'Fonte')
            
            # LINKS
            nexus_link = art.get('url')         # Link do seu site (Github Pages)
            original_link = art.get('origin_url') # Link original (CNN, G1, etc)
            image_url = art.get('image_url')
            
            # Legenda HTML Melhorada
            caption = f"<b>{desk} | {source}</b>\n\n"
            caption += f"🚀 <b>{title}</b>\n\n"
            caption += f"<i>{art.get('ai_summary', 'Resumo indisponível.')}</i>\n\n"
            
            # Área de Links (Botões de Texto)
            caption += f"🔗 <a href='{nexus_link}'>Ler Análise Completa</a>\n"
            if original_link:
                caption += f"🌍 <a href='{original_link}'>Acessar Fonte Original</a>"

            # TENTATIVA 1: Enviar COM FOTO
            success = False
            if image_url and "http" in image_url:
                try:
                    r = requests.post(
                        f"https://api.telegram.org/bot{token}/sendPhoto",
                        json={"chat_id": chat_id, "photo": image_url, "caption": caption, "parse_mode": "HTML"}
                    )
                    if r.status_code == 200:
                        print(f"   ✅ [FOTO] Enviado: {title[:20]}...")
                        success = True
                except: pass

            # TENTATIVA 2: Enviar APENAS TEXTO (Fallback)
            if not success:
                text_fallback = caption + f"\n\n(Imagem: {image_url})"
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": text_fallback, "parse_mode": "HTML", "disable_web_page_preview": False}
                )
                print(f"   ✅ [TEXTO] Enviado (Fallback): {title[:20]}...")

            sent_count += 1
            time.sleep(3)

        except Exception as e:
            print(f"   ❌ Falha crítica: {e}")

    return sent_count > 0


def send_rejected_log(rejected_articles):
    if not rejected_articles: return

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    report = "🗑️ <b>RELATÓRIO DE NOTÍCIAS FILTRADAS (Low Score)</b>\n\n"
    
    for art in rejected_articles:
        title = art.get('headline_pt', art.get('title'))
        
        # CORREÇÃO AQUI: Usa 'or' para garantir que nunca seja None
        # Se art.get retornar None, ele usa a string "Sem análise..."
        desc = art.get('ai_summary') or "Sem análise detalhada disponível."
        
        link = art.get('origin_url') or art.get('url') # Tenta link original, senão link genérico
        score = art.get('score', 0)
        
        report += f"❌ <b>[{score}pts] {title}</b>\n"
        report += f"<i>{str(desc)[:100]}...</i>\n" # str() garante blindagem extra
        report += f"<a href='{link}'>Link da Fonte</a>\n\n"

    print(f"📉 Enviando relatório de {len(rejected_articles)} rejeitadas...")
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": report, "parse_mode": "HTML", "disable_web_page_preview": True}
        )
    except Exception as e:
        print(f"Erro ao enviar log: {e}")
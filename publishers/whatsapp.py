from twilio.rest import Client
import os
import time
import re

def clean_spam_triggers(text):
    """
    Substitui palavras que ativam filtros de spam de operadoras/WhatsApp.
    """
    if not text: return ""
    
    # Dicionário de Substituição (Palavra Perigosa -> Palavra Segura)
    replacements = {
        r"criptomoedas?": "ativos digitais",
        r"bitcoin": "BTC",
        r"lucro": "resultado",
        r"investimento": "operação",
        r"dinheiro": "recursos",
        r"golpe": "fraude",
        r"armas?": "equipamento",
        r"tiroteio": "incidente",
        r"ataque": "ação",
        r"morte": "óbito",
        r"assassinato": "crime",
        r"tráfico": "comércio ilegal",
        r"\$": "USD", # Símbolo de dólar às vezes ativa filtro
        r"R\$": "BRL"
    }
    
    # Aplica as substituições
    clean_text = text
    for pattern, replacement in replacements.items():
        clean_text = re.sub(pattern, replacement, clean_text, flags=re.IGNORECASE)
        
    return clean_text

def smart_truncate(content, length=250):
    if not content: return "N/A"
    content = str(content)
    if len(content) <= length: return content
    return content[:length].rsplit(' ', 1)[0] + "..."

def send_digest(articles):
    if not articles: return False

    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
    whatsapp_from = os.getenv("TWILIO_FROM")
    whatsapp_to = os.getenv("TWILIO_TO")
    
    print(f"📤 Iniciando envio de {len(articles)} cards (MODO SEGURO)...")

    # 1. Intro (Texto Simples sem emojis pesados)
    try:
        client.messages.create(
            from_=whatsapp_from, to=whatsapp_to,
            body=f"Bot News: {len(articles)} atualizacoes relevantes encontradas."
        )
        time.sleep(2)
    except Exception as e:
        print(f"❌ Erro Intro: {e}")

    # 2. Loop de Cards
    sent_count = 0
    for art in articles:
        # Preparação do Conteúdo (Limpando gatilhos)
        headline = clean_spam_triggers(art.get('headline_pt', art.get('title')))
        source = art.get('source', 'Fonte')
        img_url = art.get('image_url')
        
        # Limpamos o resumo também
        raw_summary = art.get('ai_summary', '')
        summary = clean_spam_triggers(smart_truncate(raw_summary))
        
        # LAYOUT "CLEAN" (Menos formatação para evitar flag de MKT)
        # Removemos negritos excessivos e emojis
        msg_body = f"Manchete: {headline}\n"
        msg_body += f"Fonte: {source}\n\n"
        msg_body += f"Resumo: {summary}\n\n"
        msg_body += f"Link: {art.get('url')}"

        try:
            # Lógica de Envio (Tenta Imagem -> Falha -> Texto)
            sent = False
            
            # Tentativa 1: Com Imagem (se existir e for segura)
            if img_url and img_url.startswith("http") and "gif" not in img_url:
                try:
                    message = client.messages.create(
                        from_=whatsapp_from,
                        to=whatsapp_to,
                        body=msg_body,
                        media_url=[img_url]
                    )
                    print(f"   ✅ [IMG] Enviado! SID: {message.sid}")
                    sent = True
                except:
                    pass # Falhou imagem, cai pro texto silenciosamente

            # Tentativa 2: Apenas Texto (Se img falhou ou não existe)
            if not sent:
                message = client.messages.create(
                    from_=whatsapp_from,
                    to=whatsapp_to,
                    body=msg_body
                )
                print(f"   ✅ [TXT] Enviado! SID: {message.sid}")

            sent_count += 1
            time.sleep(3) # Pausa maior para não parecer robô de spam
            
        except Exception as e:
            print(f"❌ Erro de Bloqueio/Envio: {e}")
    
    return sent_count > 0
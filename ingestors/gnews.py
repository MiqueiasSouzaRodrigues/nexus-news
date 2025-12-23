import requests
import hashlib
import os
import datetime

def fetch_gnews_articles():
    print("📡 Buscando via GNews API...")
    
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        print("⚠️ GNews Key não encontrada. Pulando.")
        return []

    # Buscamos notícias de tecnologia e negócios em PT ou EN
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "token": api_key,
        "topic": "technology", # ou 'business'
        "lang": "en",          # Mude para 'pt' se preferir focar no Brasil
        "max": 5               # Trazemos poucas para economizar cota
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        clean_articles = []
        if r.status_code == 200:
            for item in data.get("articles", []):
                # Normalização de Dados (Para ficar igual à NewsAPI)
                
                # 1. Gerar Hash Único (ID)
                url_hash = hashlib.md5(item['url'].encode()).hexdigest()
                
                # 2. Tratar Data
                published = item.get('publishedAt', str(datetime.datetime.now()))
                
                clean_articles.append({
                    "id": url_hash,
                    "title": item['title'],
                    "url": item['url'],
                    "source": item['source']['name'],
                    "published_at": published
                })
        else:
            print(f"❌ Erro GNews: {data.get('errors')}")

        return clean_articles

    except Exception as e:
        print(f"❌ Erro de conexão GNews: {e}")
        return []
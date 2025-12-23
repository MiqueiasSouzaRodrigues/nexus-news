import requests
import hashlib
import os
import datetime

def fetch_recent_news():
    print("📡 Buscando Top Headlines Brasil e Mundo (NewsAPI)...")
    
    # Estratégia Dupla:
    # 1. Top Headlines Brasil (Pega Política, Moraes, Futebol local)
    # 2. Top Headlines EUA (Pega Geopolítica, Mercado Global)
    
    clean_articles = []
    
    for country in ['br', 'us']:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": os.getenv("NEWS_API_KEY"),
            "country": country,
            "pageSize": 10 
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                for item in data.get("articles", []):
                    url_hash = hashlib.md5(item['url'].encode()).hexdigest()
                    clean_articles.append({
                        "id": url_hash,
                        "title": item['title'],
                        "url": item['url'],
                        "source": item['source']['name'],
                        "image_url": item.get('urlToImage'),
                        "published_at": item.get('publishedAt', str(datetime.datetime.now()))
                    })
        except Exception as e:
            print(f"❌ Erro NewsAPI ({country}): {e}")
            
    return clean_articles
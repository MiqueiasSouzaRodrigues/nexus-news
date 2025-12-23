import requests
import os
import hashlib
import datetime

def fetch_bing_news():
    print("📡 Buscando Categorias Diversas (Bing)...")
    
    url = "https://bing-news-search1.p.rapidapi.com/news"
    headers = {
        "x-bingapis-sdk": "true",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST_BING")
    }

    clean_articles = []
    
    # Categorias de busca
    categories = ["Politics", "Sports", "Business", "World", "ScienceAndTechnology"]
    
    for cat in categories:
        querystring = {
            "category": cat,
            "mkt": "pt-BR", 
            "safeSearch": "Off",
            "textFormat": "Raw",
            "count": 4 
        }

        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            data = response.json()
            
            for item in data.get('value', []):
                # 1. CRIA O HASH (A correção está aqui)
                url_hash = hashlib.md5(item['url'].encode()).hexdigest()
                published = item.get('datePublished', str(datetime.datetime.now()))
                
                # 2. Tenta capturar a imagem (se existir)
                image_url = None
                try:
                    if 'image' in item and 'thumbnail' in item['image']:
                        image_url = item['image']['thumbnail']['contentUrl']
                    elif 'provider' in item and item['provider']:
                        provider_img = item['provider'][0].get('image', {}).get('thumbnail', {})
                        image_url = provider_img.get('contentUrl')
                except:
                    pass

                # 3. Salva
                clean_articles.append({
                    "id": url_hash,
                    "title": item['name'],
                    "url": item['url'],
                    "source": item.get('provider', [{}])[0].get('name', 'Bing'),
                    "published_at": published,
                    "image_url": image_url
                })
        except Exception as e:
            print(f"⚠️ Erro Bing na categoria {cat}: {e}")

    return clean_articles
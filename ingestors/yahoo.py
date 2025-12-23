import requests
import os
import hashlib
import datetime

def fetch_market_news():
    print("📡 Buscando via Yahoo Finance (Big Techs)...")
    
    url = "https://yahoo-finance166.p.rapidapi.com/api/news/list"
    
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": os.getenv("RAPIDAPI_HOST_YAHOO")
    }
    
    clean_articles = []
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        data = response.json()
        
        # Yahoo retorna estrutura diferente, precisamos navegar nela
        items = data.get('data', {}).get('main', {}).get('stream', [])
        
        for item in items:
            # Filtro: Só queremos notícias que tenham URL e Título
            content = item.get('content', {})
            if not content.get('clickThroughUrl'):
                continue
                
            title = content.get('title')
            link = content.get('clickThroughUrl', {}).get('url')
            
            # Normalização
            url_hash = hashlib.md5(link.encode()).hexdigest()
            # Yahoo data vem em formato complexo, simplificamos usando current time se falhar
            pub_date = content.get('pubDate', str(datetime.datetime.now()))

            clean_articles.append({
                "id": url_hash,
                "title": title,
                "url": link,
                "source": "Yahoo Finance",
                "published_at": pub_date
            })

        return clean_articles

    except Exception as e:
        print(f"❌ Erro Yahoo Finance: {e}")
        return []
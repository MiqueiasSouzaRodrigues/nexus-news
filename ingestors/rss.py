import feedparser
import hashlib
import datetime

# Lista Poderosa de RSS (Brasil + Mundo + Esportes)
RSS_URLS = [
    # --- BRASIL / POLÍTICA / GERAL ---
    "https://g1.globo.com/rss/g1/",             # G1 Plantão
    "https://www.cnnbrasil.com.br/feed/",       # CNN Brasil
    "https://rss.uol.com.br/feed/noticias.xml", # UOL Notícias
    
    # --- MERCADO / WEALTH ---
    "https://valor.globo.com/rss/financas/",    # Valor Econômico
    "https://feeds.bloomberg.com/markets/news.xml", # Bloomberg Global
    
    # --- ESPORTES ---
    "https://ge.globo.com/rss/ge/",             # Globo Esporte
    "https://www.espn.com.br/espn/rss/news",    # ESPN
    
    # --- TECH / IA ---
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml"
]

def fetch_rss_news():
    print("📡 Buscando RSS (G1, CNN, ESPN, Valor)...")
    cleaned_articles = []

    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            # Pega só as 2 mais novas de cada fonte para garantir frescor
            for entry in feed.entries[:2]: 

             url_hash = hashlib.md5(entry.link.encode()).hexdigest()
             published = getattr(entry, 'published', str(datetime.datetime.now()))

            cleaned_articles.append({
                    "image_url": extract_image(entry),
                    "id": url_hash,
                    "title": entry.title,
                    "url": entry.link,
                    "source": feed.feed.get('title', 'RSS Source')[:20], # Limita tamanho do nome
                    "published_at": published
                })
        except Exception as e:
            print(f"⚠️ Erro RSS {url}: {e}")

    return cleaned_articles
def extract_image(entry):
    # Tenta media_content (padrão comum)
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    # Tenta media_thumbnail
    if 'media_thumbnail' in entry:
        return entry.media_thumbnail[0]['url']
    # Tenta links/enclosures (padrão podcast/news)
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link['href']
    return None

# No loop principal do RSS:

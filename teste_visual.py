from core.visual_engine import create_news_card
import os

if not os.path.exists("assets"):
    os.makedirs("assets")

# Teste 1: Título Gigante (Para testar se a fonte diminui)
dados_longo = {
    "headline_pt": "Nvidia supera todas as expectativas e se torna a empresa mais valiosa da história superando a Apple em uma reviravolta histórica do mercado",
    "desk": "MERCADO & TECH",
    "source": "Bloomberg",
    "published_at": "2025-12-22",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Jensen_Huang_%28cropped%29.jpg/640px-Jensen_Huang_%28cropped%29.jpg"
}

# Teste 2: Título Curto
dados_curto = {
    "headline_pt": "Bitcoin atinge nova máxima histórica",
    "desk": "CRIPTO",
    "source": "CoinDesk",
    "published_at": "2025-12-22",
    "image_url": None
}

print("Gerando Card Longo...")
create_news_card(dados_longo, "teste_longo.jpg")

print("Gerando Card Curto...")
create_news_card(dados_curto, "teste_curto.jpg")

print("✅ Feito! Abra 'teste_longo.jpg' e veja se o texto coube.")
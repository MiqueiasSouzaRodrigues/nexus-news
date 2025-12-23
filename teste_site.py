from dotenv import load_dotenv
import os

# 1. CARREGA AS CHAVES ANTES DE TUDO
load_dotenv()

from core.web_generator import create_static_page

# Dados Fakes
dados = {
    "id": "teste_123",
    "title": "Nvidia supera Apple e se torna a empresa mais valiosa do mundo",
    "headline_pt": "Nvidia vira a empresa mais valiosa do mundo",
    "source": "Bloomberg",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Jensen_Huang_%28cropped%29.jpg/640px-Jensen_Huang_%28cropped%29.jpg"
}

# Gerar
try:
    arquivo = create_static_page(dados)
    print(f"\n🌍 SUCESSO! Abra este arquivo no navegador:\n{arquivo}")
except Exception as e:
    print(f"❌ Erro ainda: {e}")
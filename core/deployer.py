import os
import subprocess
import time
import requests # <--- NOVO IMPORT

# Configuração do GitHub Pages
GITHUB_USER = "MiqueiasSouzaRodrigues" # Seu usuário exato
REPO_NAME = "nexus-news"
# DICA: GitHub Pages costuma forçar lowercase (letras minúsculas) na URL
BASE_URL = f"https://{GITHUB_USER.lower()}.github.io/{REPO_NAME}/public"

def push_content_to_cloud():
    """Executa comandos Git para subir os arquivos."""
    print("☁️ Iniciando Deploy para a Nuvem (GitHub Pages)...")
    try:
        subprocess.run(["git", "add", "public/*"], check=True)
        msg = f"Auto-Update: {time.strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", msg], check=False)
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        
        print("✅ Upload Git concluído!")
        return True
    except Exception as e:
        print(f"❌ Falha no Deploy Git: {e}")
        return False

def check_url_status(url):
    """Verifica se a URL já responde com 200 OK."""
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def get_public_links(card_filename, html_filename):
    if not card_filename: return None, None
    
    card_name = os.path.basename(card_filename)
    html_name = os.path.basename(html_filename)
    
    # FORÇAR MINÚSCULO NO USUÁRIO PARA EVITAR ERRO 404
    user_lower = GITHUB_USER.lower()
    
    # Monta a URL garantindo a pasta /public/
    card_url = f"https://{user_lower}.github.io/{REPO_NAME}/public/{card_name}"
    html_url = f"https://{user_lower}.github.io/{REPO_NAME}/public/{html_name}"
    
    print(f"🔍 [DEBUG] URL Gerada: {card_url}") 
    print(f"⏳ Aguardando GitHub (Pode levar até 2 min)...")
    
    # Loop de espera (30 tentativas de 5s = 2.5 minutos)
    for i in range(30): 
        if check_url_status(card_url):
            print(f"✅ [ONLINE] Imagem no ar!")
            return card_url, html_url
        
        # Feedback visual de progresso (.)
        print(".", end="", flush=True)
        time.sleep(5)
    
    print("\n⚠️ Tempo esgotado! O GitHub está lento hoje. Enviando link assim mesmo.")
    return card_url, html_url
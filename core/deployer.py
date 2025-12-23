import os
import subprocess
import time

# Configuração do GitHub Pages
# Mude para o seu usuário e repo
GITHUB_USER = "MiqueiasSouzaRodrigues"
REPO_NAME = "nexus-news"
BASE_URL = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/public"

def push_content_to_cloud():
    """
    Executa comandos Git para subir os arquivos novos para o GitHub Pages.
    Retorna True se sucesso.
    """
    print("☁️ Iniciando Deploy para a Nuvem (GitHub Pages)...")
    
    try:
        # 1. Adicionar tudo na pasta public
        subprocess.run(["git", "add", "public/*"], check=True)
        
        # 2. Commit com data/hora
        msg = f"Auto-Update: {time.strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", msg], check=False) # Check False pois pode não ter mudanças
        
        # 3. Push
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        
        print("✅ Deploy concluído! Arquivos estão online.")
        # O GitHub leva uns 30s para atualizar o cache, vamos dar uma pausa segura
        time.sleep(15) 
        return True
        
    except Exception as e:
        print(f"❌ Falha no Deploy: {e}")
        return False

def get_public_links(card_filename, html_filename):
    """
    Transforma nomes de arquivos locais em Links Públicos da Web.
    Ex: card_123.jpg -> https://usuario.github.io/repo/public/card_123.jpg
    """
    card_url = f"{BASE_URL}/{os.path.basename(card_filename)}" if card_filename else None
    html_url = f"{BASE_URL}/{os.path.basename(html_filename)}" if html_filename else None
    
    return card_url, html_url
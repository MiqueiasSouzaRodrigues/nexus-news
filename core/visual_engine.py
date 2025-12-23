from PIL import Image, ImageDraw, ImageFont
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from io import BytesIO
import textwrap
import os

# === CONFIGURAÇÕES DA MARCA ===
BRAND_NAME = "NEXUS BRIEF"
PRIMARY_COLOR = (0, 255, 150)    # Verde Neon
BG_COLOR_FALLBACK = (15, 15, 20) # Preto quase absoluto
OVERLAY_OPACITY = 190            # Mais escuro para garantir leitura (0-255)
CARD_SIZE = (1080, 1080)

# Caminhos das fontes
FONT_PATH_BOLD = "assets/Montserrat-Bold.ttf"
FONT_PATH_SEMI = "assets/Montserrat-SemiBold.ttf"
FONT_PATH_REG = "assets/Montserrat-Regular.ttf"

def load_fonts(size_title=70):
    """Carrega fontes. Permite ajustar o tamanho do título dinamicamente."""
    try:
        return {
            'cat': ImageFont.truetype(FONT_PATH_BOLD, 30),
            'title': ImageFont.truetype(FONT_PATH_BOLD, size_title),
            'source': ImageFont.truetype(FONT_PATH_SEMI, 28),
            'footer': ImageFont.truetype(FONT_PATH_REG, 26),
            'brand': ImageFont.truetype(FONT_PATH_BOLD, 40)
        }
    except:
        print("⚠️ Fontes não encontradas. Usando padrão.")
        d = ImageFont.load_default()
        return {'cat': d, 'title': d, 'source': d, 'footer': d, 'brand': d}

def fetch_and_process_background(image_url, target_size):
    width, height = target_size
    
    # Cabeçalhos que imitam um Mac real para evitar bloqueios
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }
    
    try:
        if not image_url or not image_url.startswith('http'):
            print(f"⚠️ URL inválida ou vazia: {image_url}")
            return Image.new('RGBA', target_size, BG_COLOR_FALLBACK)
            
        # verify=False ajuda a baixar de sites com SSL mal configurado
        response = requests.get(image_url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        
        # --- Lógica de Aspect Fill (Mantida igual) ---
        aspect_ratio = img.width / img.height
        target_aspect = width / height
        
        if aspect_ratio > target_aspect:
            new_height = height
            new_width = int(aspect_ratio * new_height)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            left = (new_width - width) / 2
            img = img.crop((left, 0, left + width, height))
        else:
            new_width = width
            new_height = int(new_width / aspect_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            top = (new_height - height) / 2
            img = img.crop((0, top, width, top + height))
            
        return img
        
    except Exception as e:
        print(f"⚠️ Erro REAL ao baixar imagem: {e}")
        # Retorna o fundo sólido apenas se falhar mesmo
        return Image.new('RGBA', target_size, BG_COLOR_FALLBACK)


def draw_dynamic_text(draw, text, position, max_width, max_height, font_path):
    """
    Algoritmo Inteligente: Reduz a fonte até o texto caber na área disponível.
    """
    x, y = position
    font_size = 80 # Começa grande
    min_font_size = 40 # Tamanho mínimo aceitável
    
    final_font = None
    final_lines = []
    
    # Loop de tentativa e erro para achar o tamanho ideal
    while font_size >= min_font_size:
        font = ImageFont.truetype(font_path, font_size)
        # Calcula quantos caracteres cabem por linha (aproximado)
        avg_char_width = font.getlength("A")
        chars_per_line = int(max_width / (avg_char_width * 0.9)) # 0.9 é margem de segurança
        
        lines = textwrap.wrap(text, width=chars_per_line)
        
        # Calcula altura total do bloco de texto
        # ascent + descent dá a altura real da linha
        line_height = font.getbbox("Ay")[3] + 15 
        total_height = line_height * len(lines)
        
        if total_height <= max_height:
            final_font = font
            final_lines = lines
            break # Coube!
            
        font_size -= 5 # Se não coube, diminui a fonte e tenta de novo
    
    # Se sair do loop sem fonte (texto gigante mesmo pequeno), usa a mínima
    if final_font is None:
        final_font = ImageFont.truetype(font_path, min_font_size)
        chars_per_line = int(max_width / (final_font.getlength("A") * 0.9))
        final_lines = textwrap.wrap(text, width=chars_per_line)[:6] # Corta excesso
        
    # Desenha as linhas
    current_y = y
    for line in final_lines:
        draw.text((x, current_y), line, font=final_font, fill=(255,255,255))
        current_y += final_font.getbbox("Ay")[3] + 15

def create_news_card(article_data, output_path="temp_card.jpg"):
    # 1. Definição do Título (SEGURANÇA CONTRA ERRO DE VARIÁVEL)
    # Tenta headline_pt -> title -> "Sem Título"
    raw_title = article_data.get('headline_pt') or article_data.get('title') or "Sem Título"
    title_text = raw_title.upper() # <--- AQUI ESTÁ A VARIÁVEL QUE FALTAVA
    
    print(f"🎨 Gerando card: {title_text[:20]}...")
    
    fonts = load_fonts()
    W, H = CARD_SIZE
    
    # 2. Fundo + Overlay
    # Se a URL for None (como no seu log), ele usa o BG_COLOR_FALLBACK automaticamente
    base_img = fetch_and_process_background(article_data.get('image_url'), CARD_SIZE)
    
    overlay = Image.new('RGBA', CARD_SIZE, (0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Gradiente
    for y in range(H):
        opacity = int(OVERLAY_OPACITY * (0.4 + 0.6 * (y / H)))
        draw_overlay.line([(0, y), (W, y)], fill=(0, 0, 0, min(opacity, 255)))
        
    canvas = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(canvas)
    
    # 3. Marca (Topo)
    draw.text((60, 60), BRAND_NAME, font=fonts['brand'], fill=PRIMARY_COLOR)
    
    # 4. Categoria (Tag)
    desk = article_data.get('desk', 'GERAL').upper()
    cat_bbox = draw.textbbox((0, 0), desk, font=fonts['cat'])
    cat_w = cat_bbox[2] - cat_bbox[0]
    cat_h = cat_bbox[3] - cat_bbox[1]
    
    cat_x, cat_y = 60, 550 
    pad = 20
    draw.rectangle([(cat_x, cat_y), (cat_x + cat_w + pad*2, cat_y + cat_h + pad)], fill=PRIMARY_COLOR)
    draw.text((cat_x + pad, cat_y + 5), desk, font=fonts['cat'], fill=(0,0,0))
    
    # 5. Manchete Dinâmica (AQUI O ERRO ACONTECIA)
    # Agora 'title_text' já existe (foi definido na linha 4 desta função)
    draw_dynamic_text(
        draw, 
        title_text, # <--- Agora o Python sabe o que é isso
        position=(60, cat_y + 80), 
        max_width=W - 120,         
        max_height=300,  
        font_path=FONT_PATH_BOLD
    )
    
    # 6. Rodapé (Fonte e Data)
    source = article_data.get('source', 'Desconhecido')
    date_raw = str(article_data.get('published_at', ''))[:10] # Garante string
    
    draw.text((60, H - 100), f"{source} • {date_raw}", font=fonts['source'], fill=(200,200,200))
    
    # 7. Barra Inferior de Marca
    draw.rectangle([(0, H-40), (W, H)], fill=PRIMARY_COLOR)
    draw.text((W - 350, H - 100), "IA CURATED BRIEF", font=fonts['footer'], fill=PRIMARY_COLOR)

    # Finalização
    final_img = canvas.convert("RGB")
    final_img.save(output_path, quality=95)
    print(f"✅ Card salvo em: {output_path}")
    return output_path
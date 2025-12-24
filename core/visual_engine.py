import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import core.ai_artist as ai_artist

# --- CONFIGURAÇÕES ---
CARD_SIZE = (1080, 1350) 
WEB_SIZE = (1280, 720)   # Novo formato para o site (16:9)
PRIMARY_COLOR = (0, 255, 127) 
OVERLAY_OPACITY = 200

# Fontes (ajuste os nomes se necessário)
FONT_BOLD = "arialbd.ttf"
FONT_REG = "arial.ttf"

def load_fonts():
    try:
        return {
            'brand': ImageFont.truetype(FONT_BOLD, 40),
            'cat': ImageFont.truetype(FONT_BOLD, 35),
            'title': ImageFont.truetype(FONT_BOLD, 85), # Ajustado
            'source': ImageFont.truetype(FONT_REG, 30),
            'footer': ImageFont.truetype(FONT_BOLD, 25)
        }
    except:
        default = ImageFont.load_default()
        return {k: default for k in ['brand', 'cat', 'title', 'source', 'footer']}

def download_image(url):
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGBA")
    except Exception as e:
        print(f"❌ Erro download imagem: {e}")
        return None

def draw_dynamic_text(draw, text, position, max_width, max_height, font_path):
    x, y = position
    font_size = 85
    min_font_size = 40
    color = "white"
    
    while font_size >= min_font_size:
        font = ImageFont.truetype(font_path, font_size)
        lines = []
        words = text.split()
        current_line = words[0]
        
        valid = True
        for word in words[1:]:
            bbox = draw.textbbox((0, 0), current_line + " " + word, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        # Check height
        bbox_h = draw.textbbox((0, 0), "Aj", font=font)
        line_h = (bbox_h[3] - bbox_h[1]) * 1.2
        total_h = len(lines) * line_h
        
        if total_h <= max_height:
            curr_y = y
            for line in lines:
                draw.text((x, curr_y), line, font=font, fill=color)
                curr_y += line_h
            return
        
        font_size -= 5
    
    # Fallback
    draw.text((x, y), text[:50]+"...", font=ImageFont.truetype(font_path, min_font_size), fill=color)

def create_news_assets(article_data, output_path_card, output_path_web):
    """
    Gera DOIS assets visuais distintos:
    1. Web Image (16:9) - Limpa, cinematic.
    2. Social Card (4:5) - Vertical, com texto e branding.
    """
    
    # ---------------------------------------------------------
    # 1. GERAÇÃO WEB (Horizontal - 16:9)
    # ---------------------------------------------------------
    web_prompt = f"Cinematic wide shot, {article_data['title']}, highly detailed landscape, depth of field"
    web_url = ai_artist.generate_editorial_image(web_prompt, width=WEB_SIZE[0], height=WEB_SIZE[1])
    
    web_img = download_image(web_url)
    if web_img:
        web_img = web_img.convert("RGB")
        web_img.save(output_path_web, quality=90)
        print(f"✅ Imagem Web salva: {output_path_web}")
    else:
        # Fallback se falhar: cria preta
        Image.new('RGB', WEB_SIZE, (20,20,20)).save(output_path_web)

    # ---------------------------------------------------------
    # 2. GERAÇÃO SOCIAL (Vertical - 4:5)
    # ---------------------------------------------------------
    social_prompt = f"Vertical editorial photography, {article_data['title']}, center focus, magazine cover style"
    social_url = ai_artist.generate_editorial_image(social_prompt, width=CARD_SIZE[0], height=CARD_SIZE[1])
    
    card_img = download_image(social_url)
    if not card_img:
        card_img = Image.new('RGBA', CARD_SIZE, (20,20,20,255))
    
    # --- DESIGN DO CARD (TEXTO E OVERLAY) ---
    fonts = load_fonts()
    W, H = CARD_SIZE
    
    # Overlay Escuro (Gradiente)
    overlay = Image.new('RGBA', CARD_SIZE, (0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    for y in range(H):
        opacity = int(OVERLAY_OPACITY * (0.3 + 0.7 * (y / H)))
        draw_overlay.line([(0, y), (W, y)], fill=(0, 0, 0, min(opacity, 255)))
    
    canvas = Image.alpha_composite(card_img, overlay)
    draw = ImageDraw.Draw(canvas)
    
    # Elementos
    draw.text((60, 60), "NEXUS BRIEF", font=fonts['brand'], fill=PRIMARY_COLOR)
    
    # Categoria
    desk = article_data.get('desk', 'NEWS').upper()
    cat_bbox = draw.textbbox((0, 0), desk, font=fonts['cat'])
    draw.rectangle([(60, 550), (60 + (cat_bbox[2]-cat_bbox[0]) + 40, 550 + (cat_bbox[3]-cat_bbox[1]) + 20)], fill=PRIMARY_COLOR)
    draw.text((80, 555), desk, font=fonts['cat'], fill="black")
    
    # Título
    raw_title = article_data.get('headline_pt') or article_data.get('title')
    draw_dynamic_text(draw, raw_title.upper(), (60, 630), W-120, 500, FONT_BOLD)
    
    # Rodapé
    source = f"{article_data.get('source', 'Fonte')} • {str(article_data.get('published_at', ''))[:10]}"
    draw.text((60, H - 100), source, font=fonts['source'], fill=(200,200,200))
    
    final_card = canvas.convert("RGB")
    final_card.save(output_path_card, quality=95)
    print(f"✅ Social Card salvo: {output_path_card}")

    return output_path_card, output_path_web
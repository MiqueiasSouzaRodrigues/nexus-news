import urllib.parse
import random

def generate_editorial_image(context_text, width=1080, height=1350):
    """
    Gera URL de imagem com dimensões personalizadas via Pollinations.ai.
    """
    if not context_text: return None

    # Limita o prompt para não quebrar a URL
    base_prompt = " ".join(context_text.split()[:20])
    
    # Modificadores visuais para estilo "High-End Tech Magazine"
    style = "editorial photography, cinematic lighting, hyperrealistic, 8k, shot on 35mm lens, depth of field"
    
    full_prompt = f"{base_prompt}, {style}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    seed = random.randint(1, 999999)
    
    # A mágica acontece aqui: Width e Height dinâmicos
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}&model=flux"
    
    print(f"🎨 [IA] Gerando ({width}x{height}): '{base_prompt}...'")
    return image_url
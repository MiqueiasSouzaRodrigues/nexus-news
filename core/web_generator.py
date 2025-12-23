from groq import Groq
import os
import datetime

# Template HTML Minimalista e Moderno (Estilo Medium/Bloomberg)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <style>
        body {{ font-family: 'Georgia', serif; line-height: 1.8; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: #f9f9f9; }}
        header {{ text-align: center; padding: 40px 0; border-bottom: 1px solid #ddd; margin-bottom: 40px; }}
        .brand {{ font-family: 'Helvetica', sans-serif; font-weight: bold; color: #00ff96; text-transform: uppercase; letter-spacing: 2px; background: #000; padding: 5px 10px; display: inline-block; }}
        h1 {{ font-family: 'Helvetica', sans-serif; font-size: 2.5em; line-height: 1.2; margin-bottom: 10px; color: #111; }}
        .meta {{ color: #666; font-size: 0.9em; font-family: sans-serif; }}
        .hero-img {{ width: 100%; height: auto; border-radius: 8px; margin-bottom: 30px; }}
        .content {{ font-size: 1.1em; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
        h2 {{ margin-top: 30px; font-family: 'Helvetica', sans-serif; }}
        p {{ margin-bottom: 20px; }}
        .footer {{ text-align: center; margin-top: 50px; color: #888; font-size: 0.8em; }}
    </style>
</head>
<body>
    <header>
        <div class="brand">Nexus Brief</div>
        <h1>{headline}</h1>
        <div class="meta">Publicado em {date} • Fonte: {source}</div>
    </header>
    
    <main class="content">
        {image_tag}
        
        {body_content}
    </main>

    <div class="footer">
        &copy; 2025 Nexus Brief AI. Notícia gerada automaticamente.
    </div>
</body>
</html>
"""

def generate_full_article_content(article_data):
    """Usa a IA para escrever um artigo completo baseado no resumo."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""
    Você é um jornalista sênior de tecnologia e mercado.
    
    Baseado nesta notícia: "{article_data.get('title')}"
    Fonte original: {article_data.get('source')}
    
    ESCREVA UM ARTIGO COMPLETO (400-600 palavras) em formato HTML simples (use tags <p>, <h2>, <ul>).
    
    Estrutura:
    1. Uma introdução impactante (Lead).
    2. Seção "O Que Aconteceu": Detalhes técnicos e factuais.
    3. Seção "Análise de Mercado": Impacto nas ações, concorrentes ou setor.
    4. Seção "Visão de Futuro": O que esperar para os próximos meses.
    
    Tom de voz: Profissional, analítico, direto (Estilo Bloomberg/The Verge).
    Retorne APENAS o código HTML do corpo do texto (sem <html> ou <body>).
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Rápido e bom para texto longo
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"❌ Erro ao gerar artigo: {e}")
        return "<p>Conteúdo indisponível no momento.</p>"

def create_static_page(article_data, output_folder="public_html"):
    """Gera o arquivo .html final."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    print(f"✍️ Escrevendo artigo completo para: {article_data.get('title')[:20]}...")
    
    # 1. Gera o texto longo com IA
    full_text_html = generate_full_article_content(article_data)
    
    # 2. Prepara imagem (se tiver)
    img_tag = ""
    if article_data.get('image_url'):
        img_tag = f'<img src="{article_data["image_url"]}" class="hero-img" alt="Imagem da Notícia">'
        
    # 3. Preenche o template
    final_html = HTML_TEMPLATE.format(
        headline=article_data.get('headline_pt', article_data.get('title')),
        date=datetime.datetime.now().strftime("%d/%m/%Y"),
        source=article_data.get('source'),
        image_tag=img_tag,
        body_content=full_text_html
    )
    
    # 4. Salva o arquivo (usando o ID para nome único)
    filename = f"news_{article_data['id']}.html"
    file_path = os.path.join(output_folder, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"✅ Página gerada: {file_path}")
    return file_path
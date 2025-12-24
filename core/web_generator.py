from groq import Groq
import os
import datetime
import random
import html

VERGE_COLORS = ["#e10098", "#4602b8", "#ff4400", "#0055ff", "#00d9ff", "#ff006e"]
ARTICLE_TEMPLATES = ['minimal', 'editorial', 'magazine']

def get_common_css_js():
    """CSS e JS Premium."""
    return """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;1,9..144,300&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
        :root { 
            --accent: #e10098; 
            --text: #0a0a0a; 
            --bg: #ffffff;
            --surface: #f8f9fa;
            --border: #e1e4e8;
            --shadow: rgba(0, 0, 0, 0.1);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            overflow-x: hidden; 
            background: var(--bg); 
            color: var(--text);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .site-header {
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            padding: 24px 48px; 
            border-bottom: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            z-index: 100; 
            position: sticky; 
            top: 0;
            transition: all 0.3s;
        }
        
        .site-header.scrolled {
            padding: 16px 48px;
            box-shadow: 0 2px 20px var(--shadow);
        }
        
        .logo { 
            font-size: 1.75rem; 
            font-weight: 900; 
            letter-spacing: -1.5px; 
            text-decoration: none; 
            color: var(--text);
        }
        
        .logo span { 
            background: linear-gradient(135deg, #e10098, #ff4400);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .desktop-nav { display: flex; gap: 32px; align-items: center; }
        
        .nav-link { 
            text-decoration: none; 
            color: #555; 
            font-weight: 600; 
            font-size: 0.875rem; 
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: relative;
            padding: 8px 0;
            transition: color 0.3s;
        }
        
        .nav-link::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--accent);
            transition: width 0.3s;
        }
        
        .nav-link:hover { color: var(--accent); }
        .nav-link:hover::after { width: 100%; }

        .hamburger { 
            cursor: pointer; 
            width: 32px;
            height: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            z-index: 201;
        }
        
        .hamburger span {
            width: 100%;
            height: 3px;
            background: var(--text);
            border-radius: 2px;
            transition: all 0.3s;
        }
        
        .hamburger.active span:nth-child(1) {
            transform: translateY(10.5px) rotate(45deg);
            background: white;
        }
        
        .hamburger.active span:nth-child(2) { opacity: 0; }
        
        .hamburger.active span:nth-child(3) {
            transform: translateY(-10.5px) rotate(-45deg);
            background: white;
        }

        .sidebar {
            position: fixed; 
            top: 0; 
            right: -400px; 
            width: 380px; 
            height: 100vh;
            background: linear-gradient(135deg, #1a1a1a, #0a0a0a);
            color: #fff; 
            z-index: 200;
            padding: 60px 40px;
            transition: right 0.5s;
            display: flex; 
            flex-direction: column; 
            gap: 8px;
            box-shadow: -10px 0 40px rgba(0, 0, 0, 0.5);
            overflow-y: auto;
        }
        
        .sidebar.active { right: 0; }
        
        .sidebar-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: 199;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s;
            backdrop-filter: blur(4px);
        }
        
        .sidebar-overlay.active {
            opacity: 1;
            pointer-events: all;
        }
        
        .sidebar-close { 
            align-self: flex-end; 
            cursor: pointer; 
            font-size: 2.5rem; 
            margin-bottom: 40px;
            transition: all 0.2s;
        }
        
        .sidebar-close:hover {
            color: var(--accent);
            transform: rotate(90deg);
        }
        
        .sidebar-link { 
            color: rgba(255, 255, 255, 0.9); 
            text-decoration: none; 
            font-size: 1.75rem; 
            font-weight: 800;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
            padding: 24px 0;
            transition: all 0.3s;
        }
        
        .sidebar-link:hover { 
            color: white;
            padding-left: 12px;
        }

        .article-hero-img {
            width: 100%;
            height: 600px;
            object-fit: cover;
            object-position: center;
            display: block;
        }

        @media (max-width: 768px) {
            .desktop-nav { display: none; }
            .site-header { padding: 16px 24px; }
            .article-hero-img { height: 400px; }
            .sidebar { width: 100%; right: -100%; }
        }

        .article-container { 
            max-width: 720px; 
            margin: 0 auto; 
            padding: 60px 24px;
        }
        
        .article-meta { 
            font-family: 'Fira Code', monospace;
            color: var(--accent); 
            font-weight: 600;
            font-size: 0.8rem;
            margin-bottom: 16px; 
            display: block;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .article-title { 
            font-size: clamp(2.5rem, 6vw, 4.5rem); 
            font-weight: 900; 
            line-height: 1.05; 
            margin-bottom: 32px; 
            letter-spacing: -2.5px;
        }
        
        .article-summary {
            font-family: 'Fraunces', serif;
            font-size: 1.25rem;
            line-height: 1.6;
            color: #555;
            font-style: italic;
            margin-bottom: 48px;
            padding-left: 24px;
            border-left: 3px solid var(--accent);
        }
        
        .article-body { 
            font-family: 'Fraunces', Georgia, serif;
            font-size: 1.2rem; 
            line-height: 1.8; 
            color: #2a2a2a;
        }
        
        .article-body p { margin-bottom: 32px; }
        
        .article-body h2 { 
            font-family: 'Inter', sans-serif;
            font-weight: 800; 
            font-size: 2rem; 
            margin-top: 56px; 
            margin-bottom: 24px;
        }
    </style>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const header = document.querySelector('.site-header');
            window.addEventListener('scroll', () => {
                if (window.pageYOffset > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            });
        });
        
        function toggleMenu() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            const hamburger = document.querySelector('.hamburger');
            
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
            hamburger.classList.toggle('active');
            
            if (sidebar.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        }
        
        function closeMenu() {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('sidebar-overlay').classList.remove('active');
            document.querySelector('.hamburger').classList.remove('active');
            document.body.style.overflow = '';
        }
    </script>
    """

def get_nav_html():
    """Header e Sidebar."""
    return """
    <header class="site-header">
        <a href="index.html" class="logo">NEXUS<span>BRIEF</span></a>

        <nav class="desktop-nav">
            <a href="category_tech.html" class="nav-link">Technology</a>
            <a href="category_science.html" class="nav-link">Science</a>
            <a href="category_business.html" class="nav-link">Business</a>
            <a href="category_culture.html" class="nav-link">Culture</a>
        </nav>

        <div class="hamburger" onclick="toggleMenu()">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </header>

    <div id="sidebar-overlay" class="sidebar-overlay" onclick="closeMenu()"></div>
    
    <aside id="sidebar" class="sidebar">
        <div class="sidebar-close" onclick="closeMenu()">×</div>
        <a href="index.html" class="sidebar-link" onclick="closeMenu()">HOME</a>
        <a href="category_tech.html" class="sidebar-link" onclick="closeMenu()">TECHNOLOGY</a>
        <a href="category_science.html" class="sidebar-link" onclick="closeMenu()">SCIENCE</a>
        <a href="category_business.html" class="sidebar-link" onclick="closeMenu()">BUSINESS</a>
        <a href="category_culture.html" class="sidebar-link" onclick="closeMenu()">CULTURE</a>
        <a href="#" class="sidebar-link" onclick="closeMenu()">ABOUT</a>
    </aside>
    """

def get_article_template(template_type):
    """Templates de artigo."""
    if template_type == 'editorial':
        return """
        <style>
            .article-title { text-align: center; font-size: clamp(3rem, 7vw, 5.5rem); }
            .article-meta { text-align: center; }
            .article-summary { text-align: center; border: none; padding: 0; max-width: 600px; margin: 0 auto 48px; }
            .article-body p:first-of-type::first-letter {
                font-size: 5rem; float: left; line-height: 0.8;
                margin: 0.1em 0.1em 0 0; font-weight: 900; color: var(--accent);
            }
        </style>
        """
    elif template_type == 'magazine':
        return """
        <style>
            .article-container { max-width: 1000px; }
        </style>
        """
    return ""

def generate_full_article_content(article_data):
    """Gera conteúdo."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""Escreva artigo jornalístico sobre: "{article_data.get('title')}"
Contexto: {article_data.get('ai_summary', '')}
Estrutura: Lide + desenvolvimento + conclusão
Estilo: Narrativo, 3ª pessoa
Retorne apenas HTML (<p>, <h2>)."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2000
        )
        return completion.choices[0].message.content
    except:
        return f"<p>{html.escape(str(article_data.get('ai_summary', 'Conteúdo em processamento.')))}</p>"

def create_static_page(article_data, clean_image_filename, output_folder="public"):
    """Gera página de notícia."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    template = random.choice(ARTICLE_TEMPLATES)
    template_css = get_article_template(template)
    accent = random.choice(VERGE_COLORS)
    
    full_text_html = generate_full_article_content(article_data)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(article_data.get('headline_pt', article_data.get('title')))}</title>
    {get_common_css_js()}
    {template_css}
    <style>:root {{ --accent: {accent}; }}</style>
</head>
<body>
    {get_nav_html()}
    <img src="{clean_image_filename}" class="article-hero-img" alt="News">
    <article class="article-container">
        <span class="article-meta">/// {article_data.get('desk', 'NEWS').upper()} • {str(article_data.get('published_at', ''))[:10]}</span>
        <h1 class="article-title">{article_data.get('headline_pt', article_data.get('title'))}</h1>
        <div class="article-summary">{html.escape(str(article_data.get('ai_summary', ''))[:250])}...</div>
        <main class="article-body">{full_text_html}</main>
        <footer style="margin-top:80px; padding-top:32px; border-top:1px solid #eee;">
            <p><strong>Fonte:</strong> <a href="{article_data.get('url')}" target="_blank" style="color:var(--accent)">{article_data.get('source')}</a></p>
        </footer>
    </article>
</body>
</html>"""

    filename = f"news_{article_data['id']}.html"
    with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return os.path.join(output_folder, filename)

def generate_category_page(category, articles, output_folder="public"):
    """Gera página de categoria."""
    if not articles:
        return
    
    grid_html = ""
    for art in articles:
        grid_html += f"""
        <a href="news_{art['id']}.html" style="text-decoration:none;color:inherit;display:block;">
            <div style="overflow:hidden;border-radius:8px;margin-bottom:20px;aspect-ratio:16/10;">
                <img src="image_{art['id']}.jpg" style="width:100%;height:100%;object-fit:cover;">
            </div>
            <span style="font-size:0.7rem;color:#e10098;font-weight:700;text-transform:uppercase;">{art.get('desk', 'NEWS')}</span>
            <h3 style="font-size:1.4rem;font-weight:800;margin-top:8px;">{art.get('headline_pt', art.get('title'))}</h3>
        </a>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category.upper()} - Nexus Brief</title>
    {get_common_css_js()}
</head>
<body>
    {get_nav_html()}
    <div style="max-width:1400px;margin:0 auto;padding:80px 24px;">
        <h1 style="font-size:4rem;font-weight:900;color:#e10098;text-align:center;margin-bottom:60px;">{category.upper()}</h1>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:40px;">
            {grid_html}
        </div>
    </div>
</body>
</html>"""

    with open(os.path.join(output_folder, f"category_{category}.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_home_page(articles, output_folder="public"):
    """Gera home page."""
    if not articles:
        return
    
    valid_articles = [a for a in articles if os.path.exists(os.path.join(output_folder, f"news_{a['id']}.html"))]
    
    if not valid_articles:
        return
    
    # Gera páginas de categoria
    categories = {}
    for art in valid_articles:
        desk = art.get('desk', 'NEWS').upper()
        if desk not in categories:
            categories[desk] = []
        categories[desk].append(art)
    
    cat_map = {'TECH': 'tech', 'TECNOLOGIA': 'tech', 'SCIENCE': 'science', 'CIÊNCIA': 'science',
               'BUSINESS': 'business', 'NEGÓCIOS': 'business', 'CULTURE': 'culture', 'CULTURA': 'culture'}
    
    for desk, arts in categories.items():
        cat_slug = cat_map.get(desk, desk.lower())
        generate_category_page(cat_slug, arts, output_folder)
    
    # Home
    hero = valid_articles[0]
    others = valid_articles[1:]
    
    grid_html = ""
    for art in others:
        grid_html += f"""
        <a href="news_{art['id']}.html" style="text-decoration:none;color:inherit;display:block;">
            <div style="overflow:hidden;border-radius:8px;margin-bottom:20px;aspect-ratio:16/10;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                <img src="image_{art['id']}.jpg" style="width:100%;height:100%;object-fit:cover;transition:transform 0.5s;">
            </div>
            <span style="font-size:0.7rem;color:#e10098;font-weight:700;">{art.get('desk', 'NEWS')}</span>
            <h3 style="font-size:1.4rem;font-weight:800;margin-top:8px;">{art.get('headline_pt', art.get('title'))}</h3>
        </a>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Brief - AI Curated News</title>
    {get_common_css_js()}
</head>
<body>
    {get_nav_html()}
    <div style="max-width:1400px;margin:0 auto;padding:40px 24px;">
        <a href="news_{hero['id']}.html" style="position:relative;height:70vh;min-height:500px;display:flex;align-items:flex-end;text-decoration:none;color:white;border-radius:16px;overflow:hidden;margin-bottom:60px;box-shadow:0 10px 40px rgba(0,0,0,0.2);">
            <img src="image_{hero['id']}.jpg" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;filter:brightness(0.7);">
            <div style="position:relative;padding:60px;background:linear-gradient(to top,rgba(0,0,0,0.9),transparent);width:100%;">
                <span style="color:#e10098;font-weight:700;font-size:0.875rem;text-transform:uppercase;">// DESTAQUE</span>
                <h1 style="font-size:clamp(2.5rem,5vw,5rem);font-weight:900;line-height:1.05;margin-top:16px;">{hero.get('headline_pt', hero.get('title'))}</h1>
            </div>
        </a>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:40px;">
            {grid_html}
        </div>
    </div>
    <footer style="text-align:center;padding:80px 24px;border-top:1px solid #eee;margin-top:80px;">
        <p>&copy; 2025 Nexus Brief • AI Curated News</p>
    </footer>
</body>
</html>"""

    with open(os.path.join(output_folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
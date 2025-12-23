from datetime import datetime
import re
from core.config import SOURCE_TIERS

def clean_date_string(date_str):
    """
    Limpa sujeiras da data e traduz meses PT -> EN para o Python entender.
    """
    if not date_str: return ""
    
    # Normaliza para string
    date_str = str(date_str).strip()
    
    # Mapa de tradução PT -> EN
    meses_pt = {
        'jan': 'Jan', 'fev': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
        'mai': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
        'set': 'Sep', 'out': 'Oct', 'nov': 'Nov', 'dez': 'Dec',
        'feve': 'Feb', 'abri': 'Apr', 'agost': 'Aug' # Variações comuns
    }
    
    # Traduz meses na força bruta (case insensitive)
    lower_str = date_str.lower()
    for pt, en in meses_pt.items():
        if pt in lower_str:
            # Substitui mantendo a caixa original pode ser difícil, 
            # então vamos substituir na string original procurando o padrão
            date_str = re.sub(pt, en, date_str, flags=re.IGNORECASE)
            break # Assume que só tem um mês na string
            
    # Remove timezones que o Python odeia (EST, EDT, -0300 grudado)
    # Remove (EST), (WET), etc.
    date_str = re.sub(r'\s*\([A-Z]+\)$', '', date_str)
    # Remove "GMT" ou "UTC"
    date_str = date_str.replace('GMT', '').replace('UTC', '').strip()
    
    return date_str

def parse_date(date_str):
    """
    Parser robusto que aceita datas em Português e Inglês.
    """
    if not date_str:
        return datetime.now()

    clean_str = clean_date_string(date_str)

    # Lista de formatos possíveis
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",        # ISO (NewsAPI)
        "%Y-%m-%dT%H:%M:%S",         # ISO Simples
        "%a, %d %b %Y %H:%M:%S %z",  # RSS Padrão (Mon, 22 Dec 2025 22:00:00 +0000)
        "%a, %d %b %Y %H:%M:%S",     # RSS sem fuso
        "%Y-%m-%d %H:%M:%S",         # SQL
        "%a, %d %b %Y %H:%M %z",     # Variação curta
        # Formatos brasileiros comuns (após tradução)
        "%a, %d %b %Y %H:%M:%S %Z",  # Com timezone nomeado (EST)
        "%d %b %Y %H:%M:%S"          # Simples
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(clean_str, fmt)
            return dt.replace(tzinfo=None)
        except ValueError:
            continue
            
    # Tenta usar dateutil se instalado (é mais poderoso), senão falha silencioso
    try:
        from dateutil import parser
        return parser.parse(clean_str).replace(tzinfo=None)
    except:
        pass
    
    # Se falhar tudo, assume 'agora' mas avisa de forma limpa
    # print(f"⚠️ Data não processada: '{date_str}' -> Usando agora.") 
    return datetime.now()

def calculate_final_score(article_data, ai_data):
    # 1. Identificar Tier da Fonte
    try:
        url_parts = article_data.get('url', '').split('/')
        if len(url_parts) > 2:
            domain = url_parts[2].replace('www.', '')
        else:
            domain = 'unknown'
    except:
        domain = 'unknown'

    tier_level = SOURCE_TIERS.get(domain, "TIER_3") 
    tier_penalty = 1.0 if tier_level in ["TIER_1", "TIER_2"] else 0.5
    
    # 2. Calcular Freshness
    pub_date = parse_date(article_data.get('published_at'))
    hours_old = (datetime.now() - pub_date).total_seconds() / 3600
    if hours_old < 0: hours_old = 0
    freshness_score = max(0, 100 - (hours_old * 4))
    
    # 3. Scores IA
    editorial_score = ai_data.get('editorial_score', 50)
    impact_score = ai_data.get('impact_score', 50)
    
    # 4. Fórmula Final
    raw_score = (
        (editorial_score * 0.4) +
        (impact_score * 0.4) +
        (freshness_score * 0.2)
    )
    
    final_score = int(raw_score * tier_penalty)
    return final_score, tier_level, int(freshness_score)
# Definição de Autoridade das Fontes
SOURCE_TIERS = {
    # Tier 1 (Globais/Elite)
    "bloomberg.com": "TIER_1", "reuters.com": "TIER_1", "ft.com": "TIER_1",
    "wsj.com": "TIER_1", "economist.com": "TIER_1", "nytimes.com": "TIER_1",
    # Tier 1 (Brasil)
    "globo.com": "TIER_1", "uol.com.br": "TIER_1", "estadao.com.br": "TIER_1",
    "folha.uol.com.br": "TIER_1", "cnnbrasil.com.br": "TIER_1", "valor.globo.com": "TIER_1",
    # Tier 2 (Especializados)
    "espn.com": "TIER_2", "ge.globo.com": "TIER_2", # Esportes
    "techcrunch.com": "TIER_2", "wired.com": "TIER_2", # Tech
    "healthline.com": "TIER_2", "webmd.com": "TIER_2"  # Saúde
}

NEWS_TYPES = [
    "POLITICS",         # Política (Moraes, Leis)
    "MARKET_MOVE",      # Mercado Financeiro
    "GEOPOLITICS",      # Guerras, Relações Internacionais
    "SPORTS_UPDATE",    # Esportes
    "TECH_INNOVATION",  # IA e Tecnologia
    "HEALTH_ALERT",     # Saúde e Ciência
    "BUSINESS_DEAL"     # Negócios/Wealth
]

DESKS = [
    "POLITICA_BR", "POLITICA_INTL", 
    "MERCADO", "WEALTH", 
    "ESPORTES", "SAUDE", 
    "TECH", "GEOPOLITICA"
]
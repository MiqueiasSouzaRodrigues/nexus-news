CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT,
    source TEXT,
    published_at TEXT,
    image_url TEXT,  -- <--- NOVA COLUNA
    
    -- Campos de IA
    headline_pt TEXT,
    desk TEXT,
    news_type TEXT,
    ai_summary TEXT,
    ai_why_it_matters TEXT,
    ai_market_impact TEXT,
    
    -- Scores
    ai_editorial_score INTEGER,
    ai_impact_score INTEGER,
    freshness_score INTEGER,
    final_score INTEGER,
    source_tier TEXT,
    
    status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
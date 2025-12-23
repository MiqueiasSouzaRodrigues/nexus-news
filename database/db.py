import sqlite3
import os

DB_NAME = "news_bot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    # Only runs if DB doesn't exist
    if not os.path.exists(DB_NAME):
        with get_connection() as conn:
            with open("database/schema.sql", "r") as f:
                conn.executescript(f.read())
        print("✅ Database initialized with NEW Schema.")


def save_raw_article(article_data):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Note que adicionei image_url na query
        cursor.execute("""
            INSERT OR IGNORE INTO articles (id, title, url, source, published_at, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            article_data['id'], 
            article_data['title'], 
            article_data['url'], 
            article_data['source'], 
            article_data['published_at'],
            article_data.get('image_url') # <--- Pega a imagem ou None
        ))
        return cursor.rowcount

def get_pending_articles(limit=5):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE status='PENDING' LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

# --- THIS IS THE UPDATED FUNCTION YOU WERE MISSING ---
def update_full_analysis(article_id, ai_data, tier, final_score, fresh_score, status):
    """
    Saves the complex AI analysis into the DB.
    """
    with get_connection() as conn:
        conn.execute("""
            UPDATE articles 
            SET 
                headline_pt = ?,
                desk = ?,
                news_type = ?,
                ai_summary = ?, 
                ai_why_it_matters = ?,
                ai_market_impact = ?,
                ai_editorial_score = ?,
                ai_impact_score = ?,
                source_tier = ?,
                freshness_score = ?,
                final_score = ?,
                status = ?
            WHERE id = ?
        """, (
            ai_data.get('headline_pt'),
            ai_data.get('desk'),
            ai_data.get('news_type'),
            ai_data.get('summary_pt'),
            ai_data.get('why_it_matters'),  # <--- The key that was missing!
            ai_data.get('market_impact'),
            ai_data.get('editorial_score'),
            ai_data.get('impact_score'),
            tier,
            fresh_score,
            final_score,
            status,
            article_id
        ))

def get_ready_to_send(min_score=1):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # We explicitly verify columns to avoid errors, but SELECT * is fine if DB is new
        cursor.execute("""
            SELECT * FROM articles 
            WHERE status='ANALYZED' AND final_score >= ? 
            ORDER BY final_score DESC LIMIT 3
        """, (min_score,))
        return [dict(row) for row in cursor.fetchall()]

def mark_as_sent(article_ids):
    with get_connection() as conn:
        placeholders = ','.join('?' * len(article_ids))
        conn.execute(f"UPDATE articles SET status='SENT' WHERE id IN ({placeholders})", article_ids)


from dotenv import load_dotenv
import sys
import os

# 1. CARREGA AS SENHAS PRIMEIRO
load_dotenv()

import time
import datetime
import database.db as db
import ingestors.newsapi as newsapi
import ingestors.gnews as gnews
import ingestors.bing as bing
import core.analyzer as analyzer
import core.scoring as scoring
import core.visual_engine as visual_engine
import core.web_generator as web_generator
import core.deployer as deployer
import publishers.telegram as telegram

# Configurações
PUBLIC_FOLDER = "public"
if not os.path.exists(PUBLIC_FOLDER):
    os.makedirs(PUBLIC_FOLDER)

INTERVALO_MINUTOS = 180  # 3 horas

# Cores para logs premium
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(emoji, message, color=Colors.ENDC):
    """Sistema de log premium."""
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"{color}{emoji} [{timestamp}] {message}{Colors.ENDC}")

def separator():
    """Separador visual."""
    print(f"\n{Colors.CYAN}{'─' * 70}{Colors.ENDC}\n")

def job():
    separator()
    log("🚀", "NEXUS BRIEF - CYCLE STARTED", Colors.BOLD + Colors.HEADER)
    separator()
    
    cycle_stats = {
        'collected': 0,
        'analyzed': 0,
        'approved': 0,
        'rejected': 0,
        'deployed': 0
    }
    
    # ---------------------------------------------------------
    # 1. INGESTÃO
    # ---------------------------------------------------------
    log("📡", "PHASE 1: News Collection", Colors.BLUE)
    all_articles = []
    
    sources = [
        ("NewsAPI", newsapi.fetch_recent_news),
        ("GNews", gnews.fetch_gnews_articles),
        ("Bing", bing.fetch_bing_news)
    ]
    
    for source_name, fetch_func in sources:
        try:
            articles = fetch_func()
            all_articles.extend(articles)
            log("✓", f"{source_name}: {len(articles)} articles fetched", Colors.GREEN)
        except Exception as e:
            log("✗", f"{source_name}: Failed ({str(e)[:50]})", Colors.WARNING)
    
    if all_articles:
        for art in all_articles:
            if db.save_raw_article(art):
                cycle_stats['collected'] += 1
    
    log("📊", f"Total new articles collected: {cycle_stats['collected']}", Colors.CYAN)

    # ---------------------------------------------------------
    # 2. ANÁLISE (IA)
    # ---------------------------------------------------------
    separator()
    log("🧠", "PHASE 2: AI Analysis & Scoring", Colors.BLUE)
    
    pending = db.get_pending_articles(limit=5)
    rejected_list = []
    
    if not pending:
        log("💤", "No pending articles to analyze", Colors.WARNING)
    
    for idx, art in enumerate(pending, 1):
        log("🔍", f"Analyzing [{idx}/{len(pending)}]: {art['title'][:40]}...", Colors.CYAN)
        
        try:
            analysis = analyzer.analyze_article(art['title'], art['source'])
            
            if analysis:
                f_score, tier, fresh = scoring.calculate_final_score(art, analysis)
                
                # Régua de corte: >10 pontos aprova
                status = 'ANALYZED' if f_score > 10 else 'REJECTED'
                
                db.update_full_analysis(art['id'], analysis, tier, f_score, fresh, status)
                
                headline = analysis.get('headline_pt', art['title'])[:30]
                
                if status == 'ANALYZED':
                    cycle_stats['analyzed'] += 1
                    cycle_stats['approved'] += 1
                    log("✓", f"APPROVED: {headline} ({f_score}pts, Tier {tier})", Colors.GREEN)
                else:
                    cycle_stats['rejected'] += 1
                    log("✗", f"REJECTED: {headline} ({f_score}pts)", Colors.WARNING)
                    
                    rejected_item = dict(art)
                    rejected_item.update(analysis)
                    rejected_item['score'] = f_score
                    rejected_list.append(rejected_item)
            else:
                log("✗", f"AI analysis failed for: {art['title'][:30]}", Colors.FAIL)
                
        except Exception as e:
            log("✗", f"Error processing article: {str(e)[:50]}", Colors.FAIL)

    # ---------------------------------------------------------
    # 3. PRODUÇÃO (Design & Web)
    # ---------------------------------------------------------
    separator()
    log("🎨", "PHASE 3: Asset Production", Colors.BLUE)
    
    ready_news = db.get_ready_to_send(min_score=10)
    
    if not ready_news:
        log("💤", "No approved articles ready for production", Colors.WARNING)
    
    items_to_deploy = []
    
# ... (início do loop no orchestrator.py)
    
    for art in ready_news:
        print(f"   > Trabalhando em: {art['headline_pt'][:20]}...")
        
        # Define caminhos
        card_name = f"card_{art['id']}.jpg"   # Vertical (Instagram)
        image_name = f"image_{art['id']}.jpg" # Horizontal (Web)
        
        card_path = os.path.join(PUBLIC_FOLDER, card_name)
        image_path = os.path.join(PUBLIC_FOLDER, image_name)
        
        # Gera ASSETS (Chama a nova função do visual_engine)
        if not os.path.exists(card_path) or not os.path.exists(image_path):
            visual_engine.create_news_assets(art, output_path_card=card_path, output_path_web=image_path)
            
        # Gera Site HTML
        html_name = f"news_{art['id']}.html"
        # Passamos a imagem WEB (image_name) para o site
        html_path = web_generator.create_static_page(art, image_name, output_folder=PUBLIC_FOLDER)
        
        items_to_deploy.append({
            "art_db": art,
            "card_file": card_path, # Envia o CARD VERTICAL para o Telegram
            "html_file": html_path
        })
            

    # ---------------------------------------------------------
    # 3.5. HOME PAGE
    # ---------------------------------------------------------
    if items_to_deploy or ready_news:
        separator()
        log("🏠", "Updating Home Page", Colors.BLUE)
        
        try:
            recent_news = db.get_latest_news(limit=20)
            if recent_news:
                web_generator.generate_home_page(recent_news, output_folder=PUBLIC_FOLDER)
                log("✓", "Home page updated successfully", Colors.GREEN)
        except Exception as e:
            log("✗", f"Home page error: {str(e)[:50]}", Colors.FAIL)

    # Verifica se tem trabalho
    if not items_to_deploy and not rejected_list:
        separator()
        log("💤", "No new content to deploy or report", Colors.WARNING)
        log_cycle_summary(cycle_stats)
        return

    # ---------------------------------------------------------
    # 4. DEPLOY
    # ---------------------------------------------------------
    deploy_success = False
    
    if items_to_deploy:
        separator()
        log("☁️", "PHASE 4: Cloud Deployment", Colors.BLUE)
        
        try:
            deploy_success = deployer.push_content_to_cloud()
            
            if deploy_success:
                log("✓", "GitHub Pages sync successful", Colors.GREEN)
                cycle_stats['deployed'] = len(items_to_deploy)
                
                # ---------------------------------------------------------
                # 5. TELEGRAM PUBLICATION
                # ---------------------------------------------------------
                separator()
                log("📱", "PHASE 5: Telegram Publication", Colors.BLUE)
                
                final_list = []
                for item in items_to_deploy:
                    pub_img, pub_link = deployer.get_public_links(
                        item['card_file'], 
                        item['html_file']
                    )
                    
                    news_item = dict(item['art_db'])
                    news_item['origin_url'] = news_item['url']
                    news_item['url'] = pub_link
                    news_item['image_url'] = pub_img
                    
                    final_list.append(news_item)
                
                if telegram.send_digest(final_list):
                    ids = [x['id'] for x in final_list]
                    db.mark_as_sent(ids)
                    log("✓", f"{len(final_list)} articles sent to Telegram", Colors.GREEN)
                else:
                    log("✗", "Telegram delivery failed", Colors.FAIL)
                    
            else:
                log("✗", "GitHub deploy failed - Telegram send aborted", Colors.FAIL)
                
        except Exception as e:
            log("✗", f"Deploy error: {str(e)[:50]}", Colors.FAIL)

    # ---------------------------------------------------------
    # 6. RELATÓRIO DE REJEITADAS
    # ---------------------------------------------------------
    if rejected_list:
        separator()
        log("📉", "Sending Rejection Report", Colors.BLUE)
        
        try:
            telegram.send_rejected_log(rejected_list)
            log("✓", f"{len(rejected_list)} rejections logged", Colors.GREEN)
        except Exception as e:
            log("✗", f"Report error: {str(e)[:50]}", Colors.FAIL)

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    separator()
    log_cycle_summary(cycle_stats)
    separator()

def log_cycle_summary(stats):
    """Exibe resumo do ciclo."""
    log("📊", "CYCLE SUMMARY", Colors.BOLD + Colors.CYAN)
    print(f"""
    {Colors.GREEN}✓ Collected:{Colors.ENDC}  {stats['collected']} articles
    {Colors.BLUE}⚡ Analyzed:{Colors.ENDC}   {stats['analyzed']} articles
    {Colors.GREEN}✓ Approved:{Colors.ENDC}   {stats['approved']} articles
    {Colors.WARNING}✗ Rejected:{Colors.ENDC}   {stats['rejected']} articles
    {Colors.CYAN}☁️  Deployed:{Colors.ENDC}   {stats['deployed']} articles
    """)

def start_monitor():
    """Inicia o sistema de monitoramento."""
    separator()
    log("🤖", "NEXUS BRIEF PREMIUM SYSTEM", Colors.BOLD + Colors.HEADER)
    log("📡", "Initializing database...", Colors.CYAN)
    db.init_db()
    log("✓", "System ready", Colors.GREEN)
    separator()
    
    cycle_count = 0
    
    while True:
        cycle_count += 1
        log("🔄", f"Starting cycle #{cycle_count}", Colors.BOLD + Colors.BLUE)
        
        try:
            job()
        except KeyboardInterrupt:
            separator()
            log("⚠️", "System interrupted by user", Colors.WARNING)
            log("👋", "Shutting down gracefully...", Colors.CYAN)
            separator()
            break
        except Exception as e:
            separator()
            log("💥", f"Critical error in cycle: {str(e)}", Colors.FAIL)
            log("🔄", "Continuing to next cycle...", Colors.WARNING)
            separator()
        
        next_run = datetime.datetime.now() + datetime.timedelta(minutes=INTERVALO_MINUTOS)
        log("⏳", f"Next cycle at {next_run.strftime('%H:%M:%S')} ({INTERVALO_MINUTOS} min)", Colors.CYAN)
        
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    start_monitor()
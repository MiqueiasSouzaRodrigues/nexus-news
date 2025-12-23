# --- ORDEM CORRETA DE INICIALIZAÇÃO ---
from dotenv import load_dotenv
import sys
import os

# 1. CARREGA AS SENHAS PRIMEIRO DE TUDO (CRÍTICO!)
load_dotenv()

# 2. SÓ DEPOIS IMPORTA OS SEUS MÓDULOS (Que usam as senhas)
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
# import publishers.whatsapp as whatsapp
import publishers.telegram as telegram

load_dotenv()

# Pasta onde tudo será salvo para o Git pegar
PUBLIC_FOLDER = "public"
if not os.path.exists(PUBLIC_FOLDER): os.makedirs(PUBLIC_FOLDER)

INTERVALO_MINUTOS = 180 # 3 horas (Seguro para cotas)

def job():
    print(f"\n🔄 [CYCLE START] {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    # 1. INGESTÃO
    # ---------------------------------------------------------
    print("📡 1. Coletando notícias...")
    all_articles = []
    try: all_articles.extend(newsapi.fetch_recent_news())
    except: pass
    try: all_articles.extend(gnews.fetch_gnews_articles())
    except: pass
    try: all_articles.extend(bing.fetch_bing_news())
    except: pass
    
    # Salva no DB
    new_count = 0
    if all_articles:
        for art in all_articles:
            if db.save_raw_article(art): new_count += 1
            
    print(f"   > Novos itens brutos: {new_count}")

    # 2. ANÁLISE (IA)
    # ---------------------------------------------------------
    print("🧠 2. Analisando backlog...")
    pending = db.get_pending_articles(limit=5) # Processa 5 por vez
    
    for art in pending:
        analysis = analyzer.analyze_article(art['title'], art['source'])
        if analysis:
            f_score, tier, fresh = scoring.calculate_final_score(art, analysis)
            status = 'ANALYZED' if f_score > 30 else 'REJECTED'
            db.update_full_analysis(art['id'], analysis, tier, f_score, fresh, status)
            print(f"   > Processado: {analysis.get('headline_pt')[:30]} ({f_score}pts)")
        else:
            print(f"   > Falha IA: {art['title'][:20]}")

    # 3. PRODUÇÃO CRIATIVA (Visual + Web)
    # ---------------------------------------------------------
    print("🎨 3. Produzindo Assets (Design & Web)...")
    ready_news = db.get_ready_to_send(min_score=30)
    
    items_to_deploy = []
    
    for art in ready_news:
        print(f"   > Trabalhando em: {art['headline_pt'][:20]}...")
        
        # A. Gerar Card Visual (Salva em /public)
        card_name = f"card_{art['id']}.jpg"
        card_path = os.path.join(PUBLIC_FOLDER, card_name)
        # Só gera se não existir ainda
        if not os.path.exists(card_path):
            visual_engine.create_news_card(art, output_path=card_path)
            
        # B. Gerar Página HTML (Salva em /public)
        html_name = f"news_{art['id']}.html"
        html_path = web_generator.create_static_page(art, output_folder=PUBLIC_FOLDER)
        
        # Guardamos os caminhos para usar no deploy
        items_to_deploy.append({
            "art_db": art,
            "card_file": card_path,
            "html_file": html_path
        })

    if not items_to_deploy:
        print("zzz Nada aprovado para publicar.")
        return

    # 4. DEPLOY (Upload para Nuvem)
    # ---------------------------------------------------------
    print("☁️ 4. Sincronizando com GitHub Pages...")
    if deployer.push_content_to_cloud():
        
  # 5. DISTRIBUIÇÃO (Telegram)
    # ---------------------------------------------------------
     print("🚀 5. Enviando para o Telegram...")

    final_list_for_telegram = []

    for item in items_to_deploy:
        pub_img, pub_link = deployer.get_public_links(item['card_file'], item['html_file'])

        news_item = dict(item['art_db']) 
        news_item['image_url'] = pub_img 
        news_item['url'] = pub_link      

        final_list_for_telegram.append(news_item)

    # MUDANÇA AQUI: Chama telegram.send_digest em vez de whatsapp
    if telegram.send_digest(final_list_for_telegram):
        ids = [x['id'] for x in final_list_for_telegram]
        db.mark_as_sent(ids)
        print("✅ Ciclo completo com sucesso!")
    else:
        print("❌ Abortando envio: Falha no Upload.")

def start_monitor():
    print("🤖 NEXUS BRIEF SYSTEM ONLINE")
    db.init_db()
    while True:
        job()
        print(f"⏳ Dormindo {INTERVALO_MINUTOS} min...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    start_monitor()
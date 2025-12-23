from groq import Groq, RateLimitError
import json
import os
import time
import re
from core.config import NEWS_TYPES, DESKS

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# MUDANÇA 1: Usar um modelo mais leve e rápido para economizar cota
MODELO_PRINCIPAL = "llama-3.1-8b-instant" 

def analyze_article(title, source, full_text=""):
    """
    Transforma texto bruto em inteligência editorial com Retry Logic.
    """
    
    prompt = f"""
    Atue como Editor Chefe. Analise: "{title}" da fonte "{source}".
    
    TAREFA:
    1. Categorize CORRETAMENTE (Politics, Sports, Tech, Market, etc).
    2. Resuma em Português (max 2 frases).
    3. 'why_it_matters': Por que importa? (1 frase).
    
    SAÍDA JSON (SEM MARKDOWN):
    {{
        "headline_pt": "Título em PT",
        "desk": "ESCOLHA: [POLITICA_BR, POLITICA_INTL, MERCADO, ESPORTES, SAUDE, TECH, GEOPOLITICA]",
        "news_type": "STRATEGY_SHIFT | MARKET_MOVE | TECH_INNOVATION | RISK_ALERT | GENERAL",
        "summary_pt": "Resumo...",
        "why_it_matters": "Contexto...",
        "market_impact": "Impacto...",
        "editorial_score": 80,
        "impact_score": 80
    }}
    """
    
    # MUDANÇA 2: Retry Logic (Tenta até 3 vezes se der erro de Rate Limit)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=MODELO_PRINCIPAL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)

        except RateLimitError as e:
            # Captura o tempo de espera da mensagem de erro (ex: "Try again in 4m18s")
            error_msg = str(e)
            print(f"⚠️ Rate Limit atingido. Tentativa {attempt+1}/{max_retries}")
            
            # Tenta achar os segundos na mensagem de erro
            wait_time = 60 # Default
            match = re.search(r'try again in (\d+)m(\d+)', error_msg)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                wait_time = (minutes * 60) + seconds + 5 # +5s de segurança
            
            print(f"⏳ Dormindo por {wait_time} segundos para esfriar a API...")
            time.sleep(wait_time)
            continue # Tenta de novo
            
        except Exception as e:
            print(f"❌ Erro Irrecuperável na IA: {e}")
            return None
            
    print("❌ Falha após múltiplas tentativas.")
    return None
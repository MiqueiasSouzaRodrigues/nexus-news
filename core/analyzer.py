from groq import Groq
import os
import json

def analyze_article(title, source):
    """
    Analisa a notícia para:
    1. Validar se faz sentido (Anti-Alucinação).
    2. Corrigir a Categoria (Ex: Trailer não é Política).
    3. Gerar um resumo contexto para a imagem.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""
    Analise esta notícia: "{title}" da fonte "{source}".
    
    TAREFAS OBRIGATÓRIAS:
    1. CATEGORIA: Classifique corretamente em uma destas: TECH, SCIENCE, BUSINESS, POLITICS, ENTERTAINMENT, GAMING, SECURITY.
       (Exemplo: Filmes/Trailers = ENTERTAINMENT. Leis/Governo = POLITICS. IA/Hardware = TECH).
    2. VALIDAR: Isso parece uma notícia real e atual? Se for algo muito genérico ou parecer erro de scraping, marque como FALSE.
    3. RESUMO: Escreva um resumo de 1 parágrafo em Português.
    4. ENGLISH_CONTEXT: Um resumo curto em INGLÊS focado no visual para gerar uma imagem (Ex: "Matt Damon in a greek boat scene, cinematic movie trailer").
    
    Retorne APENAS um JSON neste formato:
    {{
        "is_valid": true,
        "desk": "CORRECT_CATEGORY",
        "headline_pt": "Título Melhorado em PT-BR",
        "ai_summary": "Resumo...",
        "image_prompt": "English visual description..."
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Erro na análise: {e}")
        return None
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

# URL do site da vitrine que será varrido
VITRINE_URL = 'https://materiais.incomumviagens.com.br/vitrine'

def realizar_web_scraping_da_vitrine():
    """
    Realiza o web scraping na URL da vitrine, extraindo o nome e a saída dos pacotes.
    Retorna uma lista de dicionários de pacotes.
    """
    pacotes = []
    
    # Adicionando um User-Agent para simular um navegador real e evitar bloqueios
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Faz a requisição HTTP com timeout
        response = requests.get(VITRINE_URL, headers=headers, timeout=15)
        response.raise_for_status() # Lança exceção para erros HTTP (4xx ou 5xx)
        
        # O tempo de espera que estava no app.py foi removido e a varredura real 
        # (que leva alguns segundos) assume a função de latência.

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Seletor: Busca por DIVs que contêm o corpo do cartão (onde estão as informações)
        # Atenção: Se a estrutura HTML da vitrine mudar, este seletor precisa ser ajustado.
        pacote_cards = soup.select('div.card-body') 
        
        id_counter = 1
        
        for card in pacote_cards:
            nome_tag = card.find('h4', class_='card-title')
            nome = nome_tag.text.strip() if nome_tag else None
            
            saida = None
            desc_tag = card.find('p', class_='card-text')
            
            if desc_tag:
                # Tenta encontrar padrões comuns como "Saída de:", ou usa o texto completo da descrição
                saida_match = re.search(r'(Saída de|Saída|Bloqueio): (.*)', desc_tag.text, re.IGNORECASE)
                
                if saida_match:
                    saida = saida_match.group(2).strip().replace('.', '')
                else:
                    saida = desc_tag.text.strip()
            
            if nome:
                # Limpeza: remove informações de datas e duração do título
                nome_limpo = re.sub(r'\|.*|\d{2}/\d{2}/\d{4}.*', '', nome).strip() 
                
                pacotes.append({
                    "id": id_counter,
                    "nome": nome_limpo,
                    "saida": saida if saida else "Consulte"
                })
                id_counter += 1
                
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO ao acessar a vitrine: {e}")
        # Em caso de falha na varredura, retorna um fallback vazio (o React trata isso)
        return [] 
        
    return pacotes

# --- Fim da Lógica de Web Scraping ---

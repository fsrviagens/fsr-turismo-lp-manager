import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time # Importação não usada, pode ser removida se não for utilizada

# URL do site da vitrine que será varrido
VITRINE_URL = 'https://materiais.incomumviagens.com.br/vitrine'

# Remover time, pois não está sendo usado
# from datetime import datetime 

def _limpar_nome_pacote(nome):
    """Limpa o nome do pacote, removendo datas, durações e separadores."""
    # 1. Remove tudo após um pipe (|) ou uma data (DD/MM/AAAA)
    nome_limpo = re.sub(r'\|.*|\d{2}/\d{2}/\d{4}.*', '', nome)
    # 2. Remove padrões como ' - X dias', ' - promoção' etc. (opcional)
    nome_limpo = re.sub(r'\s+-\s*.*', '', nome_limpo).strip()
    return nome_limpo

def _extrair_saida(desc_tag):
    """Tenta extrair a saída (origem) da tag de descrição."""
    if not desc_tag:
        return "Consulte"
        
    texto_desc = desc_tag.text.strip().replace('\n', ' ')

    # Padrão: 'Saída de:', 'Saída:', 'Bloqueio:' (com 0 ou mais espaços após os dois pontos)
    saida_match = re.search(r'(Saída de|Saída|Bloqueio):\s*(.*)', texto_desc, re.IGNORECASE)
    
    if saida_match:
        # Pega o segundo grupo (o valor após os dois pontos)
        saida = saida_match.group(2).strip().replace('.', '')
        # Se o valor for vazio após limpeza, retorna o texto completo (fallback)
        return saida if saida else texto_desc
    else:
        # Se não encontrar o padrão, retorna o texto completo da descrição como fallback
        return texto_desc

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
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Seletor: Busca por DIVs que contêm o corpo do cartão (onde estão as informações)
        pacote_cards = soup.select('div.card-body') 
        
        # Uso de enumerate para gerar o ID de forma mais pythonic, começando em 1
        for id_counter, card in enumerate(pacote_cards, 1):
            nome_tag = card.find('h4', class_='card-title')
            nome_bruto = nome_tag.text.strip() if nome_tag else None
            
            if nome_bruto:
                nome_limpo = _limpar_nome_pacote(nome_bruto)
                
                desc_tag = card.find('p', class_='card-text')
                saida = _extrair_saida(desc_tag)
                
                pacotes.append({
                    "id": id_counter,
                    "nome": nome_limpo,
                    "saida": saida
                })
                
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO ao acessar a vitrine: {e}")
        # Em caso de falha na varredura, retorna um fallback vazio (o React trata isso)
        return [] 
        
    return pacotes

# --- Fim da Lógica de Web Scraping ---
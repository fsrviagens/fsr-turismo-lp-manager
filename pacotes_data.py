import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# URL do site da vitrine que será varrido
VITRINE_URL = 'https://materiais.incomumviagens.com.br/vitrine'

# Remoção da importação 'time' não utilizada.

def _clean_number(text):
    """Limpa a string removendo caracteres não numéricos (exceto .) e converte para inteiro."""
    if not text:
        return None
        
    # Remove R$, US$, pontos (milhares) e vírgulas (decimais) para manter apenas dígitos.
    # Assumindo que o formato é R$ 1.000 (milhar com ponto, sem decimais).
    clean_str = re.sub(r'[^\d]', '', text)
    
    # Se a string estiver vazia após a limpeza, retorna None
    return int(clean_str) if clean_str else None

def _limpar_nome_pacote(nome):
    """Limpa o nome do pacote, removendo datas, durações e separadores."""
    # 1. Remove tudo após um pipe (|) ou uma data (DD/MM/AAAA)
    nome_limpo = re.sub(r'\|.*|\d{2}/\d{2}/\d{4}.*', '', nome)
    # 2. Remove padrões como ' - X dias', ' - promoção' etc.
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
        # Se não encontrar o padrão, retorna "Variável" ou a descrição completa
        return "Variável"

def realizar_web_scraping_da_vitrine():
    """
    Realiza o web scraping na URL da vitrine, extraindo nome, saída, preço parcelado
    e preço total.
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
                
                # --- NOVO BLOCO DE EXTRAÇÃO DE PREÇO E DETALHES ---
                opcoes = []
                
                # Tenta encontrar o bloco de preços assumindo a estrutura do front-end
                price_container = card.find('div', class_='pacote-price-box') 

                if price_container:
                    # 1. Extrair Preço Parcelado (valor principal)
                    parcela_tag = price_container.find('span', class_='main-price')
                    preco_parcela = _clean_number(parcela_tag.text if parcela_tag else None)

                    # 2. Extrair Preço Total (à vista)
                    total_tag = price_container.find('span', class_='price-total-cash')
                    preco_total = _clean_number(total_tag.text if total_tag else None)

                    # 3. Extrair Duração (Noites)
                    noites = "Consulte"
                    # Busca a tag de duração para extrair a informação (assumindo a classe do front-end)
                    duracao_tag = card.find('p', class_='card-duracao')

                    if duracao_tag:
                        # Regex para encontrar padrões como "7 Dias" ou "10 Noites"
                        duracao_match = re.search(r'(\d+)\s*(noites|dias)', duracao_tag.text, re.IGNORECASE)
                        if duracao_match:
                            noites = duracao_match.group(0) # Ex: "7 Dias"
                    
                    # 4. Formatar para o array 'opcoes'
                    if preco_parcela and preco_total:
                        # Assumimos 'R$' se não houver indicador de moeda mais claro
                        moeda = 'R$' 
                        if total_tag and 'US$' in total_tag.text:
                            moeda = 'USD'
                            
                        opcoes.append({
                            "preco": preco_parcela,
                            "preco_total": preco_total,
                            "noites": noites,
                            "moeda": moeda
                        })
                
                # --- FIM DA EXTRAÇÃO DE PREÇO ---

                pacotes.append({
                    "id": id_counter,
                    "nome": nome_limpo,
                    "saida": saida,
                    "opcoes": opcoes # <--- Agora contém os valores reais (se encontrados)
                })
                
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO ao acessar a vitrine: {e}")
        return [] 
        
    return pacotes

# --- Fim da Lógica de Web Scraping ---

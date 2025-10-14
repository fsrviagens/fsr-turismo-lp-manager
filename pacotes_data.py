import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# URL do site da vitrine que será varrido
VITRINE_URL = 'https://materiais.incomumviagens.com.br/vitrine'

# ... (Funções _clean_number, _limpar_nome_pacote, _extrair_saida mantidas) ...

def realizar_web_scraping_da_vitrine():
    """
    Realiza o web scraping em duas etapas: coleta os links na vitrine e 
    acessa cada link para extrair os detalhes e preços.
    """
    pacotes = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # ETAPA 1: REQUISIÇÃO DA PÁGINA PRINCIPAL (VITRINE)
        response = requests.get(VITRINE_URL, headers=headers, timeout=15)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontra o contêiner de cada pacote (assumindo que o link está logo abaixo)
        pacote_elements = soup.select('div.card') 
        
        for id_counter, element in enumerate(pacote_elements, 1):
            
            # 1. Encontrar o link da 'Lâmina de Divulgação'
            # Assumindo que a lâmina é um link (<a>) com uma classe específica ou dentro do 'card-body'
            link_tag = element.find('a', href=True) 
            
            # Tentar ser mais específico, se houver um seletor melhor.
            # Se o botão for: <a href="URL_DO_PACOTE" class="btn-lamina">
            # link_tag = element.find('a', class_='btn-lamina') 
            
            lamina_url = link_tag['href'] if link_tag else None
            
            if not lamina_url or lamina_url.startswith('#'):
                 continue # Pula este pacote se não encontrar uma URL válida
                 
            # ETAPA 2: REQUISIÇÃO DA PÁGINA INDIVIDUAL DO PACOTE (LÂMINA)
            try:
                lamina_response = requests.get(lamina_url, headers=headers, timeout=10)
                lamina_response.raise_for_status()
                lamina_soup = BeautifulSoup(lamina_response.content, 'html.parser')
            except requests.exceptions.RequestException as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO ao acessar lâmina {lamina_url}: {e}")
                continue # Pula para o próximo pacote em caso de falha
            
            # 2. Extração dos Dados do PACOTE (Agora da lamina_soup)
            
            # --- TÍTULO e SAÍDA ---
            nome_tag = lamina_soup.find('h4', class_='card-title')
            nome_bruto = nome_tag.text.strip() if nome_tag else None
            
            if not nome_bruto: continue

            nome_limpo = _limpar_nome_pacote(nome_bruto)
            desc_tag = lamina_soup.find('p', class_='card-text')
            saida = _extrair_saida(desc_tag)
            
            # --- EXTRAÇÃO DE PREÇO E DETALHES (USANDO A LÂMINA) ---
            opcoes = []
            
            # Você deve validar estes seletores com o HTML real da página da lâmina
            price_container = lamina_soup.find('div', class_='pacote-price-box') 

            if price_container:
                # 1. Extrair Preço Parcelado
                parcela_tag = price_container.find('span', class_='main-price')
                preco_parcela = _clean_number(parcela_tag.text if parcela_tag else None)

                # 2. Extrair Preço Total
                total_tag = price_container.find('span', class_='price-total-cash')
                preco_total = _clean_number(total_tag.text if total_tag else None)

                # 3. Extrair Duração
                noites = "Consulte"
                duracao_tag = lamina_soup.find('p', class_='card-duracao')

                if duracao_tag:
                    duracao_match = re.search(r'(\d+)\s*(noites|dias)', duracao_tag.text, re.IGNORECASE)
                    if duracao_match:
                        noites = duracao_match.group(0)
                
                # 4. Formatar para o array 'opcoes'
                if preco_parcela is not None and preco_total is not None:
                    moeda = 'R$' 
                    if total_tag and 'US$' in total_tag.text:
                        moeda = 'USD'
                        
                    opcoes.append({
                        "preco": preco_parcela,
                        "preco_total": preco_total,
                        "noites": noites,
                        "moeda": moeda
                    })
            
            # 3. Adicionar o pacote
            pacotes.append({
                "id": id_counter,
                "nome": nome_limpo,
                "saida": saida,
                "opcoes": opcoes
            })
                
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO geral ao acessar a vitrine: {e}")
        return [] 
        
    return pacotes
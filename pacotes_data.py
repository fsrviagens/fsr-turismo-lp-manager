import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from requests.compat import urljoin 
from PIL import Image # Necessário para processar a imagem
import io # Para manipular a imagem em memória

# IMPORTANTE: Estas linhas só funcionarão se 'pytesseract' e o motor Tesseract OCR
# estiverem instalados no ambiente de execução.
try:
    import pytesseract 
except ImportError:
    pytesseract = None
    print("Aviso: pytesseract não está instalado. A extração de preços via OCR falhará.")


# URL do site da vitrine que será varrido
VITRINE_URL = 'https://materiais.incomumviagens.com.br/vitrine'
URL_BASE = 'https://materiais.incomumviagens.com.br' # Adicionado para construir URLs absolutas

# --------------------------------------------------------------------------------
# FUNÇÕES OCR E LIMPEZA
# --------------------------------------------------------------------------------

def _clean_number_from_text(text):
    """Limpa o texto e tenta encontrar um número inteiro (valor do preço)."""
    if not text:
        return None
    
    # Remove milhar (ponto) e foca na parte inteira (antes da vírgula)
    text = text.replace('\n', ' ').strip()
    match = re.search(r'[\d\.,]+', text)
    if match:
        clean_str = match.group(0)
        clean_str = re.sub(r'\.', '', clean_str) # Remove separador de milhar
        clean_str = clean_str.split(',')[0] # Pega apenas a parte inteira (remove centavos)
        
        return int(clean_str) if clean_str.isdigit() else None
    return None

def _ocr_image_for_prices(image_url):
    """Baixa a imagem da lâmina e usa OCR para tentar extrair os preços."""
    prices = {"preco_parcela": None, "preco_total": None, "moeda": "R$"}
    
    if not pytesseract:
        return prices

    try:
        # 1. Baixar a imagem
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        
        # 2. Abrir a imagem na memória com PIL
        image = Image.open(io.BytesIO(response.content))
        
        # 3. Executar o OCR (Configurado para alta precisão em texto e números)
        full_text = pytesseract.image_to_string(
            image, 
            lang='por', 
            config='--psm 6 -c tessedit_char_whitelist=R$0123456789.,'
        )
        # Diagnóstico para monitorar a precisão do OCR no log
        print(f"OCR Texto Bruto: {full_text.strip()[:150]}...")
        
        # 4. Tentar parsear o texto
        
        # T1: Preço Total (à vista) - Busca por "à vista" seguido de valor
        total_match = re.search(r'à vista.*?(R\$|US\$)\s*([\d\.,]+)', full_text, re.IGNORECASE | re.DOTALL)
        if total_match:
             prices["preco_total"] = _clean_number_from_text(total_match.group(2))
             
        # T2: Preço Parcelado - Busca por (X) seguido de valor
        parcela_match = re.search(r'(\d+)\s*(x|X).*?(R\$|US\$)\s*([\d\.,]+)', full_text, re.IGNORECASE | re.DOTALL)
        if parcela_match:
             prices["preco_parcela"] = _clean_number_from_text(parcela_match.group(4))
        
        # Fallback (se não achou por regex): pega o primeiro e segundo número grande
        if prices["preco_parcela"] is None and prices["preco_total"] is None:
             all_numbers = re.findall(r'[\d\.,]+', full_text)
             if len(all_numbers) >= 2:
                 prices["preco_parcela"] = _clean_number_from_text(all_numbers[0])
                 prices["preco_total"] = _clean_number_from_text(all_numbers[1])


        # Determinar Moeda
        if 'US$' in full_text or 'DÓLAR' in full_text.upper():
            prices['moeda'] = 'USD'
        else:
            prices['moeda'] = 'R$'
        
    except Exception as e:
        print(f"ERRO CRÍTICO no OCR na URL {image_url}: {e}")

    return prices

# --------------------------------------------------------------------------------
# FUNÇÕES PADRÕES DE LIMPEZA
# --------------------------------------------------------------------------------

def _limpar_nome_pacote(nome):
    """Limpa o nome do pacote."""
    nome_limpo = re.sub(r'\|.*|\d{2}/\d{2}/\d{4}.*', '', nome)
    nome_limpo = re.sub(r'\s+-\s*.*', '', nome_limpo).strip()
    return nome_limpo

def _extrair_saida(desc_tag):
    """Tenta extrair a saída (origem) da tag de descrição."""
    if not desc_tag: return "Consulte"
    texto_desc = desc_tag.text.strip().replace('\n', ' ')
    saida_match = re.search(r'(Saída de|Saída|Bloqueio):\s*(.*)', texto_desc, re.IGNORECASE)
    if saida_match:
        saida = saida_match.group(2).strip().replace('.', '')
        return saida if saida else "Variável"
    else:
        return "Variável"

# --------------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# --------------------------------------------------------------------------------

def realizar_web_scraping_da_vitrine():
    pacotes = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # ETAPA 1: COLETA DOS LINKS DA VITRINE
        response = requests.get(VITRINE_URL, headers=headers, timeout=15)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'html.parser')
        pacote_elements = soup.select('div.card') 
        
        print(f"Total de cards encontrados na vitrine: {len(pacote_elements)}")
        
        for id_counter, element in enumerate(pacote_elements, 1):
            
            # 1. Encontrar o link da Lâmina (Corrigido para usar o texto do link)
            lamina_url = None
            link_tag = element.find('a', string=re.compile(r'LÂMINA DIVULGAÇÃO', re.IGNORECASE), href=True)
            
            if link_tag and link_tag.get('href'):
                lamina_url = urljoin(URL_BASE, link_tag['href'])
            
            # Valida se o link existe e se é uma imagem (png, jpg)
            if not lamina_url or not lamina_url.lower().endswith(('.png', '.jpg', '.jpeg')):
                 continue
                 
            # 2. COLETA DADOS BÁSICOS (Da página da vitrine)
            nome_tag = element.find('h4', class_='card-title')
            nome_bruto = nome_tag.text.strip() if nome_tag else None
            
            if not nome_bruto: continue

            nome_limpo = _limpar_nome_pacote(nome_bruto)
            desc_tag = element.find('p', class_='card-text')
            saida = _extrair_saida(desc_tag)
            
            # --- 3. EXECUTA O OCR PARA EXTRAIR OS PREÇOS DA IMAGEM ---
            prices = _ocr_image_for_prices(lamina_url)
            
            opcoes = []
            if prices["preco_parcela"] is not None and prices["preco_total"] is not None:
                opcoes.append({
                    "preco": prices["preco_parcela"],
                    "preco_total": prices["preco_total"],
                    "noites": "Consulte", 
                    "moeda": prices.get('moeda', 'R$')
                })
            
            if not opcoes:
                 print(f"Card {id_counter} ('{nome_limpo}'): Falha ao extrair valores com OCR.")

            # 4. Adicionar o pacote
            pacotes.append({
                "id": id_counter,
                "nome": nome_limpo,
                "saida": saida,
                "opcoes": opcoes, 
                "lamina_url": lamina_url # Mantém a URL da imagem (pode ser útil no front-end)
            })
                
    except requests.exceptions.RequestException as e:
        print(f"ERRO geral ao acessar a vitrine: {e}")
        return [] 
        
    print(f"Web Scraping + OCR finalizado. Pacotes com valores extraídos: {sum(1 for p in pacotes if p['opcoes'])}")
    return pacotes
#
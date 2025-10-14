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
        # Busca por algo como: 'à vista R$ 1.500' ou 'total USD 200'
        total_match = re.search(r'(à vista|total)\s*?(R\$|US\$)\s*([\d\.,]+)', full_text, re.IGNORECASE | re.DOTALL)
        if total_match:
             prices["preco_total"] = _clean_number_from_text(total_match.group(3))
             
        # T2: Preço Parcelado - Busca por (X) seguido de valor
        # Busca por algo como: '10x R$ 150'
        parcela_match = re.search(r'(\d+)\s*(x|X).*?(R\$|US\$)\s*([\d\.,]+)', full_text, re.IGNORECASE | re.DOTALL)
        if parcela_match:
             prices["preco_parcela"] = _clean_number_from_text(parcela_match.group(4))
        
        # Fallback (se não achou por regex): tenta pegar o primeiro e segundo número grande
        if prices["preco_parcela"] is None and prices["preco_total"] is None:
             all_numbers = re.findall(r'[\d\.,]+', full_text)
             # Limita a busca a números que parecem valores (mais de 2 dígitos)
             valid_numbers = [_clean_number_from_text(n) for n in all_numbers if _clean_number_from_text(n) and len(str(_clean_number_from_text(n))) > 2]

             if len(valid_numbers) >= 2:
                 prices["preco_parcela"] = valid_numbers[0]
                 prices["preco_total"] = valid_numbers[1]
             elif len(valid_numbers) == 1:
                 # Se só achou um valor, assume que é o total
                 prices["preco_total"] = valid_numbers[0]


        # Determinar Moeda
        if 'US$' in full_text or 'DÓLAR' in full_text.upper():
            prices['moeda'] = 'USD'
        elif 'R$' in full_text or 'REAL' in full_text.upper():
            prices['moeda'] = 'R$'
        
    except Exception as e:
        print(f"ERRO CRÍTICO no OCR na URL {image_url}: {e}")

    return prices

# --------------------------------------------------------------------------------
# FUNÇÕES PADRÕES DE LIMPEZA
# --------------------------------------------------------------------------------

def _limpar_nome_pacote(nome):
    """Limpa o nome do pacote, removendo informações de data e pipes (|)."""
    nome_limpo = re.sub(r'\|.*|\d{2}/\d{2}/\d{4}.*', '', nome)
    nome_limpo = re.sub(r'\s+-\s*.*', '', nome_limpo).strip()
    return nome_limpo

def _extrair_saida(desc_tag):
    """Tenta extrair a saída (origem) da tag de descrição."""
    if not desc_tag: return "Consulte"
    texto_desc = desc_tag.text.strip().replace('\n', ' ')
    saida_match = re.search(r'(Saída de|Saída|Bloqueio):\s*(.*)', texto_desc, re.IGNORECASE)
    if saida_match:
        # Pega o texto após o marcador de saída e tenta limpar pontuações finais
        saida = saida_match.group(2).strip().split('.')[0] 
        return saida if saida else "Variável"
    else:
        return "Variável"
        
def _gerar_desc_curta(descricao_completa):
    """Gera uma descrição curta a partir da descrição completa, focando na primeira frase."""
    if not descricao_completa:
        return "Viagem em destaque. Consulte detalhes."
    
    # Tenta pegar até o primeiro ponto final, limitando o tamanho
    primeira_frase = descricao_completa.split('.')[0]
    # Se a frase é muito longa, ou não tem ponto, limita o tamanho
    if len(primeira_frase) > 150:
         return primeira_frase[:150] + "..."
         
    return primeira_frase.strip()

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
        # Seleciona todos os 'cards' de pacote
        pacote_elements = soup.select('div.card') 
        
        print(f"Total de cards encontrados na vitrine: {len(pacote_elements)}")
        
        for id_counter, element in enumerate(pacote_elements, 1):
            
            # 1. Encontrar o link da Lâmina ("LÂMINA DIVULGAÇÃO")
            lamina_url = None
            link_tag = element.find('a', string=re.compile(r'LÂMINA DIVULGAÇÃO', re.IGNORECASE), href=True)
            
            if link_tag and link_tag.get('href'):
                lamina_url = urljoin(URL_BASE, link_tag['href'])
            
            # 2. COLETA DADOS BÁSICOS (Da página da vitrine)
            nome_tag = element.find('h4', class_='card-title')
            nome_bruto = nome_tag.text.strip() if nome_tag else None
            
            if not nome_bruto: 
                print(f"Card {id_counter}: Nome não encontrado. Pulando.")
                continue

            nome_limpo = _limpar_nome_pacote(nome_bruto)
            desc_tag = element.find('p', class_='card-text')
            
            # Captura a descrição completa, essencial para a "leitura total da página"
            descricao_completa = desc_tag.text.strip() if desc_tag else "Nenhuma descrição disponível." 
            saida = _extrair_saida(desc_tag)
            
            # --- 3. VERIFICAÇÃO E EXECUÇÃO DE OCR (apenas para links de imagem) ---
            prices = {"preco_parcela": None, "preco_total": None, "moeda": "R$"}
            should_run_ocr = False
            
            if lamina_url:
                url_lower = lamina_url.lower()
                # Verifica se a URL aponta para um arquivo de imagem
                if re.search(r'\.(png|jpg|jpeg|gif|bmp|tiff)$', url_lower):
                    should_run_ocr = True
                # Caso a lâmina seja um PDF ou outro arquivo/página, apenas registramos o URL
                elif re.search(r'\.pdf$', url_lower):
                    print(f"Card {id_counter} ('{nome_limpo}'): Lâmina é um PDF. URL registrada, OCR pulado.")
                else:
                    print(f"Card {id_counter} ('{nome_limpo}'): Lâmina não é imagem. URL registrada: {lamina_url}")
            else:
                 print(f"Card {id_counter} ('{nome_limpo}'): Não encontrou link 'LÂMINA DIVULGAÇÃO'.")

            # Executa o OCR se for uma imagem
            if should_run_ocr:
                print(f"Card {id_counter} ('{nome_limpo}'): Tentando OCR na imagem: {lamina_url}")
                prices = _ocr_image_for_prices(lamina_url)
                
            # 4. Estrutura de Opções (apenas se o OCR retornou algum dado de preço)
            opcoes = []
            if prices["preco_parcela"] is not None or prices["preco_total"] is not None:
                opcoes.append({
                    # Mantido 'preco' para compatibilidade, mas representa o valor da parcela
                    "preco": prices["preco_parcela"], 
                    "preco_total": prices["preco_total"],
                    "noites": "Consulte", 
                    "moeda": prices.get('moeda', 'R$')
                })
            
            if not opcoes and should_run_ocr:
                 print(f"Card {id_counter} ('{nome_limpo}'): Falha ao extrair valores com OCR. (Valores vazios)")

            # 5. Adicionar o pacote (Este pacote é sempre adicionado, garantindo a leitura completa)
            pacotes.append({
                "id": id_counter,
                "nome": nome_limpo,
                # Adiciona 'desc' (descrição curta) para ser usada no frontend/card de vitrine
                "desc": _gerar_desc_curta(descricao_completa), 
                "descricao_completa": descricao_completa, 
                "saida": saida,
                "opcoes": opcoes, 
                "lamina_url": lamina_url # Mantém a URL da imagem/pdf/página
            })
                
    except requests.exceptions.RequestException as e:
        print(f"ERRO geral ao acessar a vitrine: {e}")
        return [] 
        
    pacotes_com_valor = sum(1 for p in pacotes if p['opcoes'])
    print(f"Web Scraping finalizado. Total de pacotes processados: {len(pacotes)}. Pacotes com valores extraídos: {pacotes_com_valor}")
    return pacotes
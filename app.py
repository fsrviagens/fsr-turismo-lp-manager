# app.py (Versão Otimizada com Agendamento)

import os
import psycopg2
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_apscheduler import APScheduler # <-- NOVO: Para agendamento
import json # <-- NOVO: Para formatar o JSON em JS
import re # <-- NOVO: Para buscar e substituir no HTML

# Importa a função de web scraping (assume-se que ela retorna a lista completa e formatada)
from pacotes_data import realizar_web_scraping_da_vitrine

# --- Funções Auxiliares de Segurança e DB (MANTIDAS) ---

def corrigir_url_db(url):
    # ... (CORPO DA FUNÇÃO MANTIDO)
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgres://", 1)
    return url

def auth_required(f):
    # ... (CORPO DA FUNÇÃO MANTIDO)
    @wraps(f)
    def decorated(*args, **kwargs):
        AUTH_USER = os.environ.get('ADMIN_USER')
        AUTH_PASS = os.environ.get('ADMIN_PASS')
        auth = request.authorization
        if not auth or auth.username != AUTH_USER or auth.password != AUTH_PASS:
            return ('Não Autorizado. Acesso Restrito.', 401, {
                'WWW-Authenticate': 'Basic realm="Login Requerido"'
            })
        return f(*args, **kwargs)
    return decorated

# --- CONFIGURAÇÃO DO APP E AGENDADOR ---
app = Flask(__name__)
CORS(app)
scheduler = APScheduler() # Inicializa o agendador

# Define o caminho para o template HTML
# IMPORTANTE: O Flask procura por templates na pasta 'templates'
INDEX_FILE_PATH = os.path.join(app.root_path, 'templates', 'index.html')

# --- NOVO: FUNÇÃO DE AUTOMAÇÃO DE ATUALIZAÇÃO ESTATICA ---

def atualizar_vitrine_estatica():
    """
    Executa o web scraping, filtra o TOP 5 e sobrescreve o bloco de dados estáticos
    dentro do index.html.
    """
    print(f"--- [JOB AGENDADO] Iniciando atualização estática da vitrine... ---")
    start_time = time.time()
    
    try:
        # 1. Executa o Web Scraping (retorna a lista de pacotes)
        pacotes_completos = realizar_web_scraping_da_vitrine()
        
        # Lógica de Filtragem: Ordenar e pegar o Top 5
        # NOTA: O 'pacotes_completos' deve ter um campo para ordenação (ex: 'prioridade' ou 'vendas')
        
        # --- Simulação da Lógica de Top 5 (Assuma que o primeiro item é o mais vendido) ---
        # Se você não tem um campo de prioridade, apenas pegue os 5 primeiros
        top_5_pacotes = pacotes_completos[:5] 
        # --- Fim Simulação ---
        
        # 2. Adiciona o card de Consultoria (ID 999 no código JS)
        consultoria_card = {
            "id": 999, "nome": "Consultoria Personalizada / Outro Destino", 
            "saida": "Seu aeroporto de preferência", "tipo": "CONSULTORIA", 
            "desc": "✨ Destino Sob Medida: Crie seu roteiro do zero e garanta seu Desconto VIP na primeira compra com nossa consultoria especializada.", 
            "imgKey": 'Customizado'
        }
        pacotes_para_html = top_5_pacotes + [consultoria_card]

        # 3. Geração da nova string JavaScript formatada
        # O 'indent=8' ajuda a manter a legibilidade no HTML
        pacotes_js_array = json.dumps(pacotes_para_html, indent=8)
        
        # Cria a string de substituição (nome da variável deve ser a mesma do HTML)
        new_js_content = f"const DADOS_ESTATICOS_ATUALIZAVEIS = {pacotes_js_array};"

        # 4. Leitura e substituição no arquivo (index.html)
        with open(INDEX_FILE_PATH, 'r') as f:
            html_content = f.read()

        # Regex para encontrar e substituir o bloco estático no index.html
        # IMPORTANTE: O REGEX deve ser robusto para encontrar APENAS a variável
        # Ele busca: 'const DADOS_ESTATICOS_ATUALIZAVEIS = [...];'
        pattern = re.compile(r"const DADOS_ESTATICOS_ATUALIZAVEIS = \[\s*\{.*?\}\s*\];", re.DOTALL)
        
        # Substitui o bloco
        new_html_content = pattern.sub(new_js_content, html_content)

        # 5. Escrita do novo arquivo HTML
        with open(INDEX_FILE_PATH, 'w') as f:
            f.write(new_html_content)
        
        end_time = time.time()
        print(f"--- SUCESSO! Vitrine estática atualizada em {end_time - start_time:.2f}s. Total: {len(pacotes_para_html)} cards. ---")

    except Exception as e:
        print(f"--- ERRO CRÍTICO no JOB AGENDADO: Falha ao atualizar a vitrine estática. Erro: {e} ---")
        
    return # Não retorna nada, apenas executa

# --- CONFIGURAÇÃO DO AGENDAMENTO ---
def init_scheduler():
    if os.environ.get('SCHEDULER_RUNNING') != 'true':
        # Adiciona o job. Usa 'interval' de 72 horas.
        # Caso o servidor reinicie, o APScheduler garante que ele tente rodar o job
        # se o tempo de intervalo tiver passado.
        scheduler.add_job(
            id='Job_Atualizacao_Vitrine', 
            func=atualizar_vitrine_estatica, 
            trigger='interval', 
            hours=72, # <--- A CADA 3 DIAS
            start_date=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 60)) # Começa em 1 minuto
        )
        scheduler.start()
        os.environ['SCHEDULER_RUNNING'] = 'true'
        print("--- Agendador APScheduler iniciado com sucesso. Atualização a cada 72h. ---")
        
# --- ROTAS DA LANDING PAGE (MANTIDAS) ---

@app.route('/')
def index():
    return render_template('index.html')

# ... (outras rotas do frontend: politica_de_privacidade, obrigado, cadastro) ...

# ----------------------------------------------------------------------
# ENDPOINT /api/pacotes (REMOVIDO OU SIMPLIFICADO)
# Já que o frontend agora usa DADOS_ESTATICOS_ATUALIZAVEIS, este endpoint
# que faz o scraping em tempo real se torna redundante e desnecessário.
# MANTENHA-O APENAS SE HOUVER OUTROS SISTEMAS QUE O CONSUMAM.
# ----------------------------------------------------------------------
@app.route('/api/pacotes', methods=['GET'])
def get_pacotes():
    # Retorna um 404/410 para desincentivar o uso, já que a fonte é estática
    return jsonify({"message": "Este endpoint foi desativado. Use a fonte estática."}), 410

# ... (outras rotas de caputura de lead e gerenciamento: capturar_lead, leads, setup_database) ...

# --- INICIALIZAÇÃO ---

if __name__ == '__main__':
    # Inicializa o agendador ANTES de rodar o app
    init_scheduler() 
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True, use_reloader=False) 
    # use_reloader=False é importante para que o agendador não duplique o job.

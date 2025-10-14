# app.py (Versão Final e Estável)

import os
import psycopg2
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_apscheduler import APScheduler
import json 
import re 
from datetime import datetime 

# Importa a função de web scraping 
from pacotes_data import realizar_web_scraping_da_vitrine

# --- Configuração do APScheduler ---
class Config:
    SCHEDULER_API_ENABLED = False # Desativa API REST para segurança
    JOBS = [
        {
            'id': 'Job_Atualizacao_Vitrine',
            'func': 'app:atualizar_vitrine_estatica', 
            'trigger': 'interval',
            'hours': 72, 
            'start_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            'misfire_grace_time': 300 
        }
    ]

# --- CONFIGURAÇÃO DO APP E AGENDADOR ---
app = Flask(__name__)
CORS(app)

# Define o caminho para o template HTML
INDEX_FILE_PATH = os.path.join(app.root_path, 'templates', 'index.html')


# --- NOVO: FUNÇÃO DE AUTOMAÇÃO DE ATUALIZAÇÃO ESTATICA (FILTRO REMOVIDO) ---
def atualizar_vitrine_estatica():
    """
    Executa o web scraping, processa todos os pacotes encontrados e sobrescreve o bloco
    de dados estáticos dentro do index.html.
    """
    print(f"--- [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] JOB AGENDADO: Iniciando atualização estática... ---")
    start_time = time.time()
    
    try:
        # 1. Executa o Web Scraping 
        pacotes_completos = realizar_web_scraping_da_vitrine()
        
        # CORREÇÃO: Remove a limitação de [:5] para processar todos os pacotes encontrados.
        pacotes_a_serem_processados = pacotes_completos 
        
        # 2. CONFIGURAÇÃO DE CHAVES PARA O FRONT-END
        for pacote in pacotes_a_serem_processados:
            # Adiciona 'tipo' e 'imgKey' (Chaves necessárias para o React)
            pacote['tipo'] = 'NACIONAL'
            pacote['imgKey'] = pacote['nome'] 
            
            # Garante que o campo 'opcoes' existe, mesmo que esteja vazio (veio do scraper)
            if 'opcoes' not in pacote:
                 pacote['opcoes'] = [] 
            
        
        # 3. Adiciona o card de Consultoria
        consultoria_card = {
            "id": -1, "nome": "Consultoria Personalizada / Outro Destino", 
            "saida": "Seu aeroporto de preferência", "tipo": "CONSULTORIA", 
            "desc": "✨ Destino Sob Medida: Crie seu roteiro do zero e garanta seu Desconto VIP na primeira compra com nossa consultoria especializada.", 
            "imgKey": 'Customizado'
        }
        pacotes_para_html = pacotes_a_serem_processados + [consultoria_card]

        # 4. Geração da nova string JavaScript formatada
        pacotes_js_array = json.dumps(pacotes_para_html, indent=8)
        new_js_content = f"const DADOS_ESTATICOS_ATUALIZAVEIS = {pacotes_js_array};"

        # 5. Leitura e substituição no arquivo (index.html)
        with open(INDEX_FILE_PATH, 'r') as f:
            html_content = f.read()

        # Regex AJUSTADO: 
        pattern = re.compile(
            r"const DADOS_ESTATICOS_ATUALIZAVEIS\s*=\s*\[.*?\]\s*;", 
            re.DOTALL
        )
        
        # Substitui o bloco
        new_html_content = pattern.sub(new_js_content, html_content)

        # 6. Escrita do novo arquivo HTML
        with open(INDEX_FILE_PATH, 'w') as f:
            f.write(new_html_content)
        
        end_time = time.time()
        print(f"--- SUCESSO! Vitrine estática atualizada em {end_time - start_time:.2f}s. Total: {len(pacotes_para_html)} cards. ---")

    except Exception as e:
        print(f"--- [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERRO CRÍTICO no JOB AGENDADO: {e} ---")
        
    return 

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


app.config.from_object(Config()) # Carrega a configuração do agendador

scheduler = APScheduler() 
scheduler.init_app(app)


# --- ROTAS DA LANDING PAGE (MANTIDAS) ---

@app.route('/')
def index():
    return render_template('index.html')

# ... (outras rotas do frontend: politica_de_privacidade, obrigado, cadastro) ...

# ----------------------------------------------------------------------
# ENDPOINT /api/pacotes 
# ----------------------------------------------------------------------
@app.route('/api/pacotes', methods=['GET'])
def get_pacotes():
    # Retorna um 410 (Gone) para indicar que a funcionalidade foi removida/movida
    return jsonify({"message": "Este endpoint foi desativado. A vitrine agora é carregada via dados estáticos no HTML."}), 410

# ... (outras rotas de caputura de lead e gerenciamento: capturar_lead, leads, setup_database) ...

# --- INICIALIZAÇÃO ---

if __name__ == '__main__':
    # Inicializa o agendador APENAS no processo principal, após carregar as configurações.
    if os.environ.get('SCHEDULER_RUNNING') != 'true':
        scheduler.start()
        os.environ['SCHEDULER_RUNNING'] = 'true'
        print("--- Agendador APScheduler iniciado com sucesso. ---")
        
    # use_reloader=False é mantido para evitar duplicação do job em ambientes DEV.
    # Debug=False é recomendado para produção.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=False, use_reloader=False)

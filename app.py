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


# --- NOVAS FUNÇÕES AUXILIARES PARA PROCESSAMENTO DE DADOS ---

def _determinar_tipo_pacote(nome_pacote):
    """
    Determina se o pacote é NACIONAL ou INTERNACIONAL com base em palavras-chave no nome.
    O React usa essa chave para definir o ícone (plane-departure vs globe-americas).
    """
    # Lista de palavras-chave que indicam destino internacional
    destinos_internacionais = ['tailândia', 'egito', 'turquia', 'europa', 'orlando', 'caribe', 'cancun', 'dubai', 'asia', 'américas', 'méxico', 'chile', 'peru', 'argentina', 'colômbia']
    nome_pacote_lower = nome_pacote.lower()
    
    if any(di in nome_pacote_lower for di in destinos_internacionais):
        return 'INTERNACIONAL'
    
    return 'NACIONAL' 

def _gerar_img_key(nome_pacote):
    """
    Gera uma chave de imagem para mapeamento no React, correspondente às chaves 
    definidas no bloco const IMAGENS do index.html.
    """
    nome_lower = nome_pacote.lower()
    
    # Mapeamento para as chaves que existem no bloco const IMAGENS do index.html
    # Chaves de referência: 'Lençóis Maranhenses', 'Tailândia', 'Gramado', 'Porto de Galinhas', 'Salvador', 'Egito', 'Turquia', 'Customizado'
    mapeamento_simples = {
        'lençóis maranhenses': 'Lençóis Maranhenses',
        'tailândia': 'Tailândia',
        'gramado': 'Gramado',
        'porto de galinhas': 'Porto de Galinhas',
        'maragogi': 'Porto de Galinhas', # Sinônimo
        'salvador': 'Salvador',
        'egito': 'Egito',
        'turquia': 'Turquia',
    }
    
    for palavra_chave, img_key in mapeamento_simples.items():
        if palavra_chave in nome_lower:
            return img_key
            
    # Fallback
    return 'Customizado'

# ----------------------------------------------------------------------


# --- FUNÇÃO DE AUTOMAÇÃO DE ATUALIZAÇÃO ESTATICA ---
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
            # AJUSTE CRÍTICO: Adiciona 'tipo' e 'imgKey' dinamicamente
            pacote['tipo'] = _determinar_tipo_pacote(pacote['nome'])
            pacote['imgKey'] = _gerar_img_key(pacote['nome'])
            
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
    """
    Função mantida para compatibilidade com variáveis de ambiente.
    """
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgres://", 1)
    return url

def auth_required(f):
    """
    Função mantida para autenticação de rotas administrativas.
    """
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

# ====================================================================
# CORREÇÃO CRÍTICA PARA AMBIENTES DE PRODUÇÃO (GUNICORN/RAILWAY)
# Inicializa o Agendador aqui, fora do bloco if __name__ == '__main__', 
# para que ele seja iniciado corretamente pelo Gunicorn/Processo Master.
# ====================================================================
scheduler.start() 
print("--- Agendador APScheduler iniciado com sucesso. ---")


# --- ROTAS DA LANDING PAGE (MANTIDAS) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/politica-de-privacidade.html')
def politica_de_privacidade():
    return render_template('politica-de-privacidade.html')

@app.route('/obrigado.html')
def obrigado():
    return render_template('obrigado.html')

@app.route('/cadastro.html')
def cadastro():
    return render_template('cadastro.html')

# ----------------------------------------------------------------------
# ENDPOINT /api/pacotes 
# ----------------------------------------------------------------------
@app.route('/api/pacotes', methods=['GET'])
def get_pacotes():
    # Retorna um 410 (Gone) para indicar que a funcionalidade foi removida/movida
    return jsonify({"message": "Este endpoint foi desativado. A vitrine agora é carregada via dados estáticos no HTML."}), 410

# --- ROTAS DE CAPTURA DE LEAD E GERENCIAMENTO (MANTIDAS) ---

@app.route('/capturar_lead', methods=['POST'])
def capturar_lead():
    # ... (Corpo da função capturar_lead) ...
    
    # ----------------------------------------------------------------------
    # CONEXÃO E INSERÇÃO NO BANCO DE DADOS (POSTGRESQL)
    # ----------------------------------------------------------------------
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
         print("Aviso: DATABASE_URL não está configurada. Lead não será salvo no DB.")
         return jsonify({"message": "Lead capturado com sucesso (sem DB)."}, 200)

    try:
        data = request.get_json()
        
        nome = data.get('nome')
        telefone = data.get('telefone')
        pacote_selecionado = data.get('pacoteSelecionado')
        data_viagem = data.get('dataViagem')
        passageiros = data.get('passageiros')
        origem_lead = data.get('origem_lead', 'Desconhecida')
        data_captura = data.get('data_captura', datetime.now().isoformat())
        
        # Sanitize data
        telefone = re.sub(r'[^0-9]', '', str(telefone))
        passageiros = int(passageiros) if isinstance(passageiros, (str, int)) and str(passageiros).isdigit() else 1
        
        db_url = corrigir_url_db(DATABASE_URL)
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute(
            """
            INSERT INTO leads (nome, telefone, pacote_selecionado, data_viagem, passageiros, origem_lead, data_captura)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nome, telefone, pacote_selecionado, data_viagem, passageiros, origem_lead, data_captura)
        )
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Lead capturado com sucesso e salvo no DB."}), 200

    except psycopg2.Error as e:
        print(f"Erro ao salvar o lead no banco de dados: {e}")
        return jsonify({"message": "Erro interno ao salvar lead no DB.", "error": str(e)}, 500)
    except Exception as e:
        print(f"Erro inesperado na captura de lead: {e}")
        return jsonify({"message": "Erro inesperado.", "error": str(e)}, 500)
    
@app.route('/leads.html')
@auth_required
def leads():
    # ... (Corpo da função leads) ...
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({"error": "DATABASE_URL não configurada."}), 500
        
    leads_list = []
    try:
        db_url = corrigir_url_db(DATABASE_URL)
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("SELECT id, nome, telefone, pacote_selecionado, data_viagem, passageiros, data_captura, origem_lead FROM leads ORDER BY data_captura DESC LIMIT 50")
        
        leads_data = cur.fetchall()
        
        # Obtém os nomes das colunas
        column_names = [desc[0] for desc in cur.description]
        
        # Cria uma lista de dicionários para facilitar a exibição
        for row in leads_data:
            lead = dict(zip(column_names, row))
            # Formata a data de captura
            if isinstance(lead['data_captura'], datetime):
                lead['data_captura'] = lead['data_captura'].strftime('%d/%m/%Y %H:%M:%S')
            leads_list.append(lead)

        cur.close()
        conn.close()

        # renderiza o template de gerenciamento
        return render_template('leads.html', leads=leads_list)

    except psycopg2.Error as e:
        print(f"Erro ao buscar leads: {e}")
        return jsonify({"error": "Erro ao conectar ou buscar no banco de dados."}, 500)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({"error": "Erro inesperado."}, 500)


@app.route('/setup_database', methods=['POST'])
@auth_required
def setup_database():
    # ... (Corpo da função setup_database) ...
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({"message": "DATABASE_URL não está configurada."}, 500)

    try:
        db_url = corrigir_url_db(DATABASE_URL)
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone VARCHAR(15) NOT NULL,
                pacote_selecionado TEXT,
                data_viagem DATE,
                passageiros INTEGER,
                data_captura TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                origem_lead VARCHAR(100)
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Banco de dados e tabela 'leads' configurados com sucesso."}), 200

    except psycopg2.Error as e:
        return jsonify({"message": f"Erro ao configurar o banco de dados: {e}"}, 500)
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {e}"}, 500)
    

# --- INICIALIZAÇÃO (APENAS PARA USO DE DESENVOLVIMENTO LOCAL) ---

if __name__ == '__main__':
    # Este bloco só é executado quando rodado com 'python app.py' localmente.
    # O Gunicorn (produção) IGNORA este bloco.
    # O scheduler já foi iniciado acima.
    print("--- Modo de Desenvolvimento Local (Executando app.run) ---")
    
    # Se quiser forçar a atualização da vitrine ao iniciar em DEV:
    # atualizar_vitrine_estatica() 
    
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True, use_reloader=False)

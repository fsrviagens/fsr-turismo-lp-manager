import os
import psycopg2
import time
# smtplib e outras bibliotecas de e-mail removidas
from functools import wraps 
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS 
from pacotes_data import realizar_web_scraping_da_vitrine 

# --- Funções Auxiliares de Segurança e DB ---

def corrigir_url_db(url):
    """
    Corrige o esquema da URL do banco de dados para ser compatível com o psycopg2.
    """
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgres://", 1)
    return url

def auth_required(f):
    """
    Decorador personalizado para exigir autenticação HTTP Basic.
    As credenciais são definidas nas variáveis de ambiente ADMIN_USER e ADMIN_PASS.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # As credenciais devem ser definidas como variáveis de ambiente no Railway
        AUTH_USER = os.environ.get('ADMIN_USER')
        AUTH_PASS = os.environ.get('ADMIN_PASS')
        
        # Tenta obter as credenciais da requisição
        auth = request.authorization
        
        # Verifica se as credenciais estão corretas
        if not auth or auth.username != AUTH_USER or auth.password != AUTH_PASS:
            # Retorna o código 401 e exige o login Basic Auth
            return ('Não Autorizado. Acesso Restrito.', 401, {
                'WWW-Authenticate': 'Basic realm="Login Requerido"'
            })
            
        return f(*args, **kwargs)
    return decorated

# Função enviar_alerta_lead removida


# --- Configuração do App ---
app = Flask(__name__)
CORS(app) 
# --- Fim da Configuração do App ---


# --- ROTAS DA LANDING PAGE (FRONTEND) ---

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a Política de Privacidade
@app.route('/politica-de-privacidade.html')
def politica_de_privacidade():
    return render_template('politica-de-privacidade.html')

# Rota para a página de Obrigado
@app.route('/obrigado.html')
def obrigado():
    return render_template('obrigado.html')

# Rota para a página de Cadastro
@app.route('/cadastro.html')
def cadastro():
    return render_template('cadastro.html')


# ENDPOINT: Rota para buscar os Pacotes
@app.route('/api/pacotes', methods=['GET'])
def get_pacotes():
    
    start_time = time.time() 
    
    try:
        # 1. Executa o Web Scraping real
        pacotes_atuais = realizar_web_scraping_da_vitrine()

        end_time = time.time() 
        elapsed_time = end_time - start_time
        
        MIN_DELAY = 2.0 
        
        if elapsed_time < MIN_DELAY:
            time.sleep(MIN_DELAY - elapsed_time)
            
        return jsonify(pacotes_atuais), 200

    except Exception as e:
        print(f"ERRO CRÍTICO no endpoint /api/pacotes: {e}")
        return jsonify({"message": "Falha na varredura. Retornando lista vazia."}), 500


# Rota para capturar o Lead
@app.route('/capturar_lead', methods=['POST'])
def capturar_lead():
    data = request.json 
    
    nome = data.get('nome', 'N/A')
    whatsapp = data.get('telefone', 'N/A')
    destino = data.get('pacoteSelecionado', 'N/A')

    try:
        pessoas = data.get('passageiros')
        data_viagem_input = data.get('dataViagem')
        data_viagem = data_viagem_input if data_viagem_input else None 
        
        email = None
        tipo_viagem = None
        orcamento = None
        
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        
        if db_url_corrigida:
            conn = psycopg2.connect(db_url_corrigida)
            cur = conn.cursor()
            
            cur.execute(
                """
                INSERT INTO cadastro (nome, email, whatsapp, tipo_viagem, destino, orcamento, pessoas, data_viagem) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (nome, email, whatsapp, tipo_viagem, destino, orcamento, pessoas, data_viagem)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            print("SUCESSO: Lead salvo no BD.")
        else:
            print("AVISO: DATABASE_URL não configurada. Lead NÃO SALVO no BD.")
        
        # O alerta de e-mail foi removido.
        
        return jsonify({'success': True, 'message': 'Lead salvo com sucesso!'}), 200

    except Exception as e:
        print(f"ERRO DE BANCO DE DADOS/SERVIDOR: {e}")
        
        # O código de tentativa de envio de alerta em caso de falha de BD foi removido.
        return jsonify({'success': False, 'message': f'Erro no servidor ao salvar lead: {str(e)}'}), 500 # Retorna 500 para erro de servidor.


# --- ROTAS DE GERENCIAMENTO ---

# Rota para a página de leads (AGORA PROTEGIDA)
@app.route('/leads.html', methods=['GET'])
@auth_required # <--- Decorador de segurança aplicado aqui!
def leads():
    try:
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        if not db_url_corrigida:
            error_message = [("ERRO: DATABASE_URL não configurada.", "", "", "", "")]
            return render_template('leads.html', leads=error_message), 500
            
        conn = psycopg2.connect(db_url_corrigida)
        cur = conn.cursor()
        
        cur.execute("SELECT nome, whatsapp, destino, pessoas, data_viagem FROM cadastro ORDER BY nome")
        leads_data = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('leads.html', leads=leads_data)
        
    except Exception as e:
        print(f"Erro ao carregar leads: {e}")
        error_message = [(f"ERRO AO CONECTAR/CONSULTAR BD: {str(e)}", "", "", "", "")]
        return render_template('leads.html', leads=error_message), 500

# Rota para configurar o banco de dados (Manutenção)
@app.route('/setup')
def setup_database():
    try:
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        if not db_url_corrigida:
            raise ValueError("DATABASE_URL não está configurada.")
            
        conn = psycopg2.connect(db_url_corrigida)
        cur = conn.cursor()
        
        # Garante a existência das colunas necessárias
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS pessoas INTEGER;")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS data_viagem DATE;")


        conn.commit()
        cur.close()
        conn.close()
        
        return "Tabela 'cadastro' verificada e atualizada com sucesso com as colunas necessárias (pessoas, data_viagem)! ", 200
    except Exception as e:
        return f"Erro ao configurar o banco de dados: {e}", 500

# --- INICIALIZAÇÃO ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)

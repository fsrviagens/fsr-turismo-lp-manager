import os
import psycopg2
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import json 
import re 
from datetime import datetime 
from supabase import create_client, Client # NOVO: Importação para o cliente Supabase

# --- CONFIGURAÇÃO DO APP E CLIENTE SUPABASE ---

app = Flask(__name__)
CORS(app)

# Define o caminho para o template HTML
# INDEX_FILE_PATH não é mais necessário, pois não faremos mais a escrita estática
# INDEX_FILE_PATH = os.path.join(app.root_path, 'templates', 'index.html')


# --- INICIALIZAÇÃO DO CLIENTE SUPABASE (PACOTES) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("--- Cliente Supabase (Pacotes e Auth) inicializado com sucesso. ---")
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível inicializar o cliente Supabase: {e}")
else:
    print("AVISO: Variáveis SUPABASE_URL ou SUPABASE_KEY não configuradas. Acesso ao DB de pacotes será desativado.")


# --- FUNÇÕES AUXILIARES ---

def corrigir_url_db(url):
    """
    Função mantida para compatibilidade com variáveis de ambiente do PostgreSQL para Leads.
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
        # NOTA: O Supabase Auth poderia ser usado aqui para login mais seguro, 
        # mas mantive o método Basic Auth existente (ADMIN_USER/ADMIN_PASS) por enquanto.
        AUTH_USER = os.environ.get('ADMIN_USER')
        AUTH_PASS = os.environ.get('ADMIN_PASS')
        auth = request.authorization
        if not auth or auth.username != AUTH_USER or auth.password != AUTH_PASS:
            return ('Não Autorizado. Acesso Restrito.', 401, {
                'WWW-Authenticate': 'Basic realm="Login Requerido"'
            })
        return f(*args, **kwargs)
    return decorated


# --- FUNÇÕES AUXILIARES PARA PROCESSAMENTO DE DADOS (SIMPLIFICADAS) ---

def _determinar_tipo_pacote(nome_pacote):
    """
    Mantido para consistência, mas o ideal é ter 'tipo' como campo no DB.
    """
    destinos_internacionais = ['tailândia', 'egito', 'turquia', 'europa', 'orlando', 'caribe', 'cancun', 'dubai', 'asia', 'américas', 'méxico', 'chile', 'peru', 'argentina', 'colômbia']
    nome_pacote_lower = nome_pacote.lower()
    
    if any(di in nome_pacote_lower for di in destinos_internacionais):
        return 'INTERNACIONAL'
    
    return 'NACIONAL' 

def _gerar_img_key(nome_pacote):
    """
    Mantido para consistência, mas o ideal é que esta chave venha diretamente do DB.
    """
    nome_lower = nome_pacote.lower()
    
    # Mapeamento para as chaves que existem no bloco const IMAGENS do index.html
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
            
    return 'Customizado'

# ----------------------------------------------------------------------
# ** FUNÇÃO atualizar_vitrine_estatica() E APSCHEDULER REMOVIDOS **
# ----------------------------------------------------------------------


# --- ROTAS DA LANDING PAGE ---

@app.route('/')
def index():
    pacotes = []
    
    if supabase_client:
        try:
            # Busca do Supabase: Pacotes ATIVOS, ordenados por 'ordem'
            response = supabase_client.table("pacotes").select("*").eq('ativo', True).order('ordem', desc=False).execute()
            
            # CORREÇÃO V2: Usa verificação robusta para garantir que pacotes seja sempre uma lista
            pacotes = response.data if response and hasattr(response, 'data') and response.data is not None else []

            # Aplica lógica de tipo/chave de imagem se necessário (melhor que venha do DB)
            for pacote in pacotes:
                if 'tipo' not in pacote:
                    pacote['tipo'] = _determinar_tipo_pacote(pacote.get('nome', ''))
                if 'imgKey' not in pacote:
                    pacote['imgKey'] = _gerar_img_key(pacote.get('nome', ''))
            
        except Exception as e:
            print(f"ERRO: Falha ao buscar pacotes no Supabase para a landing page: {e}")
            # Em caso de erro, a lista de pacotes permanece vazia []
    
    # Adiciona o card de Consultoria
    consultoria_card = {
        "id": -1, 
        "nome": "Consultoria Personalizada / Outro Destino", 
        "saida": "Seu aeroporto de preferência", 
        "tipo": "CONSULTORIA", 
        "desc": "✨ Destino Sob Medida: Crie seu roteiro do zero e garanta seu Desconto VIP na primeira compra com nossa consultoria especializada.", 
        "imgKey": 'Customizado'
    }
    
    if pacotes is not None:
         pacotes.append(consultoria_card)

    # CORREÇÃO: Serializa a lista 'pacotes' para JSON e a passa com a chave 'pacotes_json' 
    # que o React no index.html espera ler.
    return render_template('index.html', pacotes_json=json.dumps(pacotes))

@app.route('/politica-de-privacidade.html')
def politica_de_privacidade():
    return render_template('politica-de-privacidade.html')

@app.route('/obrigado.html')
def obrigado():
    return render_template('obrigado.html')

@app.route('/cadastro.html')
def cadastro():
    return render_template('cadastro.html')


# --- ROTAS ADMINISTRATIVAS DE PACOTES (CRUD) ---

@app.route('/admin')
def admin_redirect():
    # Redireciona o acesso base para a listagem de pacotes
    return redirect(url_for('admin_pacotes_index'))

@app.route('/admin/pacotes')
@auth_required
def admin_pacotes_index():
    if not supabase_client:
        return render_template('admin_erro.html', error="Cliente Supabase não inicializado.")
        
    try:
        # Busca todos os pacotes (ativos e inativos)
        response = supabase_client.table("pacotes").select("*").order('id', desc=True).execute()
        
        # --- CORREÇÃO FINAL: Garante que 'pacotes' é uma lista, mesmo se a resposta for None, 
        # --- não tiver o atributo 'data', ou se 'data' for None. Isso resolve o erro 'NoneType'.
        pacotes = response.data if response and hasattr(response, 'data') and response.data is not None else []
        # ------------------------------------------------------------------------------------------------------------------
        
        # Renderiza a tabela de gerenciamento (index)
        return render_template('admin_pacotes_index.html', pacotes=pacotes)
        
    except Exception as e:
        # Este bloco agora deve capturar qualquer erro remanescente de conexão/permissão
        return render_template('admin_erro.html', error=f"Erro ao listar pacotes: {e}")


@app.route('/admin/pacotes/novo', methods=['GET', 'POST'])
@auth_required
def admin_pacotes_form(pacote_id=None):
    if not supabase_client:
        return render_template('admin_erro.html', error="Cliente Supabase não inicializado.")
        
    pacote = {} # Inicializa como dicionário vazio para o template

    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Converte o checkbox 'ativo' para booleano
        ativo_status = 'ativo' in data 
        
        pacote_data = {
            "nome": data.get('nome_pacote'), 
            "destino": data.get('destino'),
            "saida": data.get('saida'),
            "desc": data.get('descricao'),
            "preco_antigo": data.get('preco_antigo'),
            "preco_atual": data.get('preco_atual'),
            "url_saibamais": data.get('url_saibamais'),
            "imagem_url": data.get('imagem_url'), # Deve ser a URL do Supabase Storage
            "imgKey": data.get('imgKey'),
            "tipo": data.get('tipo'),
            "ordem": int(data.get('ordem', 99)),
            "ativo": ativo_status
        }
        
        try:
            # INSERT: Ação de 'Novo'
            response = supabase_client.table("pacotes").insert(pacote_data).execute()
            print(f"Pacote inserido com sucesso: {response.data}")
            return redirect(url_for('admin_pacotes_index'))
            
        except Exception as e:
            return render_template('admin_erro.html', error=f"Erro ao inserir pacote: {e}") 
    
    # GET: Exibe o formulário vazio para criação
    return render_template('admin_pacotes_form.html', pacote=pacote, title="Novo Pacote")


@app.route('/admin/pacotes/editar/<int:pacote_id>', methods=['GET', 'POST'])
@auth_required
def admin_pacotes_editar(pacote_id):
    if not supabase_client:
        return render_template('admin_erro.html', error="Cliente Supabase não inicializado.")
        
    try:
        # Busca o pacote pelo ID
        response = supabase_client.table("pacotes").select("*").eq('id', pacote_id).single().execute()
        pacote = response.data
    except Exception:
        return render_template('admin_erro.html', error=f"Pacote ID {pacote_id} não encontrado.")

    if request.method == 'POST':
        data = request.form.to_dict()
        ativo_status = 'ativo' in data 
        
        pacote_data = {
            "nome": data.get('nome_pacote'), 
            "destino": data.get('destino'),
            "saida": data.get('saida'),
            "desc": data.get('descricao'),
            "preco_antigo": data.get('preco_antigo'),
            "preco_atual": data.get('preco_atual'),
            "url_saibamais": data.get('url_saibamais'),
            "imagem_url": data.get('imagem_url'),
            "imgKey": data.get('imgKey'),
            "tipo": data.get('tipo'),
            "ordem": int(data.get('ordem', 99)),
            "ativo": ativo_status
        }
        
        try:
            # UPDATE: Atualiza o pacote
            supabase_client.table("pacotes").update(pacote_data).eq('id', pacote_id).execute()
            return redirect(url_for('admin_pacotes_index'))
        except Exception as e:
            return render_template('admin_erro.html', error=f"Erro ao editar pacote: {e}") 
    
    # GET: Exibe o formulário preenchido para edição
    return render_template('admin_pacotes_form.html', pacote=pacote, title=f"Editar Pacote: {pacote.get('nome')}")


@app.route('/admin/pacotes/excluir/<int:pacote_id>', methods=['POST'])
@auth_required
def admin_pacotes_excluir(pacote_id):
    if not supabase_client:
        return jsonify({"message": "Cliente Supabase não inicializado."}, 500)
    
    try:
        supabase_client.table("pacotes").delete().eq('id', pacote_id).execute()
        return redirect(url_for('admin_pacotes_index'))
    except Exception as e:
        return jsonify({"message": f"Erro ao excluir pacote: {e}"}, 500)


# --- ROTAS DE CAPTURA DE LEAD E GERENCIAMENTO (MANTIDAS) ---

@app.route('/capturar_lead', methods=['POST'])
def capturar_lead():
    # ... (Corpo da função capturar_lead - MANTIDO INALTERADO) ...
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
    # ... (Corpo da função leads - MANTIDO INALTERADO) ...
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
        
        column_names = [desc[0] for desc in cur.description]
        
        for row in leads_data:
            lead = dict(zip(column_names, row))
            if isinstance(lead['data_captura'], datetime):
                lead['data_captura'] = lead['data_captura'].strftime('%d/%m/%Y %H:%M:%S')
            leads_list.append(lead)

        cur.close()
        conn.close()

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
    # ... (Corpo da função setup_database - MANTIDO INALTERADO) ...
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        return jsonify({"message": "DATABASE_URL não está configurada."}, 500)

    try:
        db_url = corrigir_url_db(DATABASE_URL)
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Cria a tabela de leads (PostgreSQL)
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
        
        # NOTA: A tabela 'pacotes' deve ser criada DIRETAMENTE no painel do Supabase.
        
        return jsonify({"message": "Banco de dados e tabela 'leads' configurados com sucesso. (Tabela 'pacotes' deve ser criada no Supabase)"}), 200

    except psycopg2.Error as e:
        return jsonify({"message": f"Erro ao configurar o banco de dados: {e}"}, 500)
    except Exception as e:
        return jsonify({"message": f"Erro inesperado: {e}"}, 500)
    

# --- INICIALIZAÇÃO (APENAS PARA USO DE DESENVOLVIMENTO LOCAL) ---

# ESTE BLOCO FOI COMENTADO PARA GARANTIR QUE APENAS O GUNICORN INICIE A APLICAÇÃO EM PRODUÇÃO.
# if __name__ == '__main__':
#     # Nenhum agendador para iniciar aqui.
#     print("--- Modo de Desenvolvimento Local (Executando app.run) ---")
#     app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True, use_reloader=False)

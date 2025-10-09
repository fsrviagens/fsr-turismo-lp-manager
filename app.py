import os
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, url_for

# --- Funções Auxiliares ---

def corrigir_url_db(url):
    """
    Corrige o esquema da URL do banco de dados para ser compatível com o psycopg2.
    O Render usa 'postgresql://', mas o psycopg2 (e alguns ambientes) preferem 'postgres://'.
    """
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgres://", 1)
    return url

# --- Configuração do App ---
app = Flask(__name__)

# --- ROTAS DA LANDING PAGE (REACT FRONTEND) ---

# Rota para servir a página principal (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para capturar o Lead (Endpoint da Automação)
@app.route('/capturar_lead', methods=['POST'])
def capturar_lead():
    data = request.json 

    try:
        # Mapeamento e Tratamento de Campos do Formulário
        nome = data.get('nome')
        whatsapp = data.get('telefone')
        destino = data.get('pacoteSelecionado')
        pessoas = data.get('passageiros')
        
        # Garante que string vazia ('') se torne None (NULL no BD)
        data_viagem_input = data.get('dataViagem')
        data_viagem = data_viagem_input if data_viagem_input else None 
        
        # Campos que o novo formulário NÃO coleta (inseridos como NULL)
        email = None
        tipo_viagem = None
        orcamento = None
        
        # Conectar ao banco de dados com a correção da URL
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        
        if not db_url_corrigida:
            raise ValueError("DATABASE_URL não está configurada no ambiente.")

        conn = psycopg2.connect(db_url_corrigida)
        cur = conn.cursor()
        
        # Inserir os dados na tabela 'cadastro'
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
        
        # Retorna sucesso para o Frontend (que então abrirá o WhatsApp)
        return jsonify({'success': True, 'message': 'Lead salvo com sucesso!'}), 200

    except Exception as e:
        # Fluxo de Falha Elegante: Retorna 200 para que o frontend abra o WhatsApp
        print(f"ERRO DE BANCO DE DADOS/SERVIDOR: {e}")
        return jsonify({'success': False, 'message': f'Erro no servidor ao salvar lead: {str(e)}'}), 200 


# --- ROTAS DE GERENCIAMENTO ---

# Rota para a página de leads (mantida)
@app.route('/leads.html', methods=['GET'])
def leads():
    try:
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        if not db_url_corrigida:
            raise ValueError("DATABASE_URL não está configurada.")
            
        conn = psycopg2.connect(db_url_corrigida)
        cur = conn.cursor()
        
        cur.execute("SELECT nome, whatsapp, destino, pessoas, data_viagem FROM cadastro ORDER BY nome")
        leads_data = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('leads.html', leads=leads_data)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Rota para configurar o banco de dados (Manutenção)
@app.route('/setup')
def setup_database():
    try:
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        if not db_url_corrigida:
            raise ValueError("DATABASE_URL não está configurada.")
            
        conn = psycopg2.connect(db_url_corrigida)
        cur = conn.cursor()
        
        # Garante a existência da coluna 'pessoas'
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS pessoas INTEGER;")

        conn.commit()
        cur.close()
        conn.close()
        
        return "Tabela 'cadastro' verificada e atualizada com sucesso com as colunas necessárias!", 200
    except Exception as e:
        return f"Erro ao configurar o banco de dados: {e}", 500

# --- INICIALIZAÇÃO ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)

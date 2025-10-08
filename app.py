import os
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

# --- ROTAS DA LANDING PAGE (REACT FRONTEND) ---

# Rota para servir a página principal (index.html)
@app.route('/')
def index():
    # Esta página agora contém o código React (JSX) e o formulário
    return render_template('index.html')

# Rota para capturar o Lead (Endpoint da Automação)
# O frontend React enviará os dados para esta rota via JSON (fetch/POST)
@app.route('/capturar_lead', methods=['POST'])
def capturar_lead():
    # O React envia dados via JSON, então usamos request.json
    data = request.json 

    try:
        # Mapeamento dos campos do novo formulário (React) para os campos do BD ('cadastro')
        nome = data.get('nome')
        whatsapp = data.get('telefone') # O campo 'telefone' do React vai para a coluna 'whatsapp'
        destino = data.get('pacoteSelecionado') # O 'pacoteSelecionado' do React vai para a coluna 'destino'
        pessoas = data.get('passageiros')
        data_viagem = data.get('dataViagem') or None # Usa None se for string vazia
        
        # Campos que o novo formulário NÃO coleta (são inseridos como NULL)
        email = None
        tipo_viagem = None
        orcamento = None
        
        # Conectar ao banco de dados usando as variáveis de ambiente
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Inserir os dados na tabela 'cadastro'
        # Note o uso de %s para NULL para os campos não coletados
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
        # Em caso de falha no banco, ainda assim informamos para o frontend continuar
        # com o fluxo do WhatsApp, para não perder o cliente.
        print(f"ERRO DE BANCO DE DADOS: {e}")
        return jsonify({'success': False, 'message': f'Erro no servidor ao salvar lead: {str(e)}'}), 500


# --- ROTAS DE GERENCIAMENTO (MANTIDAS) ---

# Rota para a página de leads (mantida)
@app.route('/leads.html', methods=['GET'])
def leads():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Ajuste o SELECT para mostrar as colunas mais relevantes do novo formulário
        cur.execute("SELECT nome, whatsapp, destino, pessoas, data_viagem FROM cadastro ORDER BY nome")
        leads_data = cur.fetchall()
        cur.close()
        conn.close()
        
        # ATENÇÃO: Se o leads.html original esperava 8 colunas, pode ser necessário 
        # ajustar o loop no leads.html para esperar apenas as 5 colunas acima.
        return render_template('leads.html', leads=leads_data)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Rota para configurar o banco de dados (Mantida para fins de manutenção)
@app.route('/setup')
def setup_database():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Adiciona as colunas uma por uma para garantir que a tabela seja atualizada corretamente
        # É importante que a coluna 'whatsapp' já exista, assim como 'destino', 'pessoas', 'data_viagem'
        # O restante do código pode ser mantido se for apenas para fins de migração:
        # cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(255);")
        # ... (etc)
        
        # Apenas um comando de exemplo para garantir a coluna 'pessoas' (que corresponde a passageiros)
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS pessoas INTEGER;")

        conn.commit()
        cur.close()
        conn.close()
        
        return "Tabela 'cadastro' verificada e atualizada com sucesso com as colunas necessárias!", 200
    except Exception as e:
        return f"Erro ao configurar o banco de dados: {e}", 500

# --- ROTAS ANTIGAS (REMOVIDAS / COMENTADAS) ---
# As rotas abaixo foram removidas pois a nova Landing Page usa o endpoint /capturar_lead e o WhatsApp.

# @app.route('/cadastro.html', methods=['GET'])
# def cadastro():
#     return render_template('cadastro.html')

# @app.route('/obrigado.html', methods=['GET'])
# def obrigado():
#     return render_template('obrigado.html')

# @app.route('/processa_cadastro', methods=['POST'])
# def processa_cadastro():
#     # Rota antiga de processamento de formulário - SUBSTITUÍDA por /capturar_lead
#     pass

if __name__ == '__main__':
    # Quando rodando em produção (com gunicorn), a variável de ambiente DEBUG será False.
    # Para testes no Termux, pode ser útil manter debug=True.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)

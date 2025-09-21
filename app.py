import os
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Rota para a página inicial (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de cadastro (cadastro.html)
@app.route('/cadastro.html', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')

# Rota para a página de leads
@app.route('/leads.html', methods=['GET'])
def leads():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        cur.execute("SELECT nome, email, senha FROM cadastro ORDER BY nome")
        leads = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('leads.html', leads=leads)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Rota para o processamento do formulário de cadastro
@app.route('/processa_cadastro', methods=['POST'])
def processa_cadastro():
    try:
        # Tenta ler os dados do formulário HTML primeiro
        data = request.form
        
        # Se não houver dados de formulário, tenta ler JSON (para compatibilidade futura)
        if not data:
            data = request.json
        
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        
        if not nome or not email or not senha:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400

        # Conectar ao banco de dados usando as variáveis de ambiente do Render
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Inserir os dados na tabela 'cadastro'
        cur.execute("INSERT INTO cadastro (nome, email, senha) VALUES (%s, %s, %s)",
                    (nome, email, senha))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Retornar uma resposta de sucesso
        return jsonify({'success': True, 'message': 'Dados recebidos com sucesso!'}), 200

    except Exception as e:
        # Em caso de erro, retornar uma mensagem de erro
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/setup')
def setup_database():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Cria a tabela 'cadastro' se ela ainda não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cadastro (
                nome VARCHAR(255),
                email VARCHAR(255),
                senha VARCHAR(255)
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        return "Tabela 'cadastro' verificada/criada com sucesso!", 200
    except Exception as e:
        return f"Erro ao configurar o banco de dados: {e}", 500



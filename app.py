import os
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

# Rota para a página inicial (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página de cadastro (cadastro.html)
@app.route('/cadastro.html', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')

# Rota para a página de obrigado
@app.route('/obrigado.html', methods=['GET'])
def obrigado():
    return render_template('obrigado.html')

# Rota para a página de leads
@app.route('/leads.html', methods=['GET'])
def leads():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        cur.execute("SELECT nome, email, whatsapp, tipo_viagem, destino, orcamento, pessoas, data_viagem FROM cadastro ORDER BY nome")
        leads_data = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('leads.html', leads=leads_data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Rota para o processamento do formulário de cadastro
@app.route('/processa_cadastro', methods=['POST'])
def processa_cadastro():
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        whatsapp = request.form.get('whatsapp')
        tipo_viagem = request.form.get('tipo_viagem')
        destino = request.form.get('destino')
        orcamento = request.form.get('orcamento')
        pessoas = request.form.get('pessoas')
        data_viagem = request.form.get('data_viagem')

        # Conectar ao banco de dados usando as variáveis de ambiente do Render
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Inserir os dados na tabela 'cadastro'
        cur.execute(
            "INSERT INTO cadastro (nome, email, whatsapp, tipo_viagem, destino, orcamento, pessoas, data_viagem) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (nome, email, whatsapp, tipo_viagem, destino, orcamento, pessoas, data_viagem))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Redirecionar para a página de obrigado após o cadastro
        return redirect(url_for('obrigado'))

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Rota para configurar o banco de dados (Adiciona colunas se não existirem)
@app.route('/setup')
def setup_database():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Adiciona as colunas uma por uma para garantir que a tabela seja atualizada corretamente
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(255);")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS tipo_viagem VARCHAR(50);")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS destino VARCHAR(255);")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS orcamento VARCHAR(50);")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS pessoas VARCHAR(10);")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS data_viagem VARCHAR(255);")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;")
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return "Tabela 'cadastro' atualizada com sucesso com as novas colunas!", 200
    except Exception as e:
        return f"Erro ao configurar o banco de dados: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)

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

# Rota para o processamento do formulário de cadastro
@app.route('/processa_cadastro', methods=['POST'])
def processa_cadastro():
    try:
        data = request.json
        if not data:
            data = request.form
        
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

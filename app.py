import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuração da conexão com o banco de dados
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS")
    )
    return conn

# Rota para receber os dados do formulário
@app.route('/processa_cadastro', methods=['POST'])
def processa_cadastro():
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        telefone = dados.get('telefone')
        preferencia = dados.get('preferencia')
        destino = dados.get('destino')
        data_ida = dados.get('dataIda')
        data_volta = dados.get('dataVolta')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO clientes (nome, email, telefone, preferencia, destino, data_ida, data_volta) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nome, email, telefone, preferencia, destino, data_ida, data_volta)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Orçamento solicitado com sucesso!'})

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({'success': False, 'message': 'Erro na conexão com o banco de dados.'})

if __name__ == '__main__':
    app.run(debug=True)


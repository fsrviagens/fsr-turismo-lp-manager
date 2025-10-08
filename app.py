import os
import psycopg2
from flask import Flask, request, jsonify, render_template, redirect, url_for

# --- Configuração do App ---
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
        # Mapeamento e Tratamento de Campos do Formulário
        nome = data.get('nome')
        whatsapp = data.get('telefone') # 'telefone' do React -> 'whatsapp' do BD
        destino = data.get('pacoteSelecionado') # 'pacoteSelecionado' do React -> 'destino' do BD
        pessoas = data.get('passageiros')
        
        # CORREÇÃO: Trata string vazia ('') do input de data como None (NULL no BD)
        data_viagem_input = data.get('dataViagem')
        data_viagem = data_viagem_input if data_viagem_input else None 
        
        # Campos que o novo formulário NÃO coleta (inseridos como NULL)
        email = None
        tipo_viagem = None
        orcamento = None
        
        # Conectar ao banco de dados usando as variáveis de ambiente
        # ATENÇÃO: Verifique se a variável DATABASE_URL está configurada no seu ambiente Termux/Hospedagem
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
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
        # Fluxo de Falha Elegante: O loga o erro, mas informa ao frontend que pode continuar
        # com o fluxo do WhatsApp (abrir o chat) para não perder o lead.
        print(f"ERRO DE BANCO DE DADOS: {e}")
        return jsonify({'success': False, 'message': f'Erro no servidor ao salvar lead: {str(e)}'}), 200 # Retorna 200, não 500


# --- ROTAS DE GERENCIAMENTO ---

# Rota para a página de leads (mantida)
@app.route('/leads.html', methods=['GET'])
def leads():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # O SELECT foi ajustado para mostrar APENAS os campos coletados pelo novo formulário
        cur.execute("SELECT nome, whatsapp, destino, pessoas, data_viagem FROM cadastro ORDER BY nome")
        leads_data = cur.fetchall()
        cur.close()
        conn.close()
        
        # Se o seu leads.html precisar de ajustes de colunas, você terá que fazê-los separadamente
        return render_template('leads.html', leads=leads_data)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Rota para configurar o banco de dados (Mantida para fins de manutenção)
@app.route('/setup')
def setup_database():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        # Comando para garantir a coluna 'pessoas' (que corresponde a passageiros) exista
        cur.execute("ALTER TABLE cadastro ADD COLUMN IF NOT EXISTS pessoas INTEGER;")

        conn.commit()
        cur.close()
        conn.close()
        
        return "Tabela 'cadastro' verificada e atualizada com sucesso com as colunas necessárias!", 200
    except Exception as e:
        return f"Erro ao configurar o banco de dados: {e}", 500

# --- INICIALIZAÇÃO ---

if __name__ == '__main__':
    # Usar 'gunicorn app:app' é a forma recomendada de iniciar em produção
    # Este bloco é apenas para testes locais (como no Termux)
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)

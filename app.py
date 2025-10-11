import os
import psycopg2
import time
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS 
from pacotes_data import realizar_web_scraping_da_vitrine # Importando a função de scraping real

# --- Funções Auxiliares ---

def corrigir_url_db(url):
    """
    Corrige o esquema da URL do banco de dados para ser compatível com o psycopg2.
    O Supabase/Railway usa 'postgresql://', mas o psycopg2 prefere 'postgres://'.
    """
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgres://", 1)
    return url

def enviar_alerta_lead(nome, whatsapp, destino):
    """
    Função do Robô de Prospecção: Envia um e-mail de alerta sobre o novo lead.
    Utiliza as 5 Variáveis de Ambiente SMTP configuradas no Railway.
    """
    # 1. Recupera as variáveis de ambiente
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = os.environ.get('SMTP_PORT')
    SMTP_SENDER_EMAIL = os.environ.get('SMTP_SENDER_EMAIL') # leads@fsr.tur.br
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')         # Senha de Aplicativo Zoho
    RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')       # O e-mail que recebe o alerta
    
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_SENDER_EMAIL, SMTP_PASSWORD, RECEIVER_EMAIL]):
        print("AVISO: Variáveis SMTP incompletas. Alerta de e-mail NÃO ENVIADO.")
        return

    try:
        # 2. Monta o corpo do e-mail
        subject = f"🔔 NOVO LEAD FSR - {nome} ({destino})"
        body = f"""
        Olá, você recebeu um novo Lead da FSR Viagens:

        - Nome: {nome}
        - WhatsApp: {whatsapp}
        - Destino Selecionado: {destino}
        
        Acesse o painel de leads para mais detalhes.
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        # 3. Conecta e envia o e-mail via Zoho Mail (ou outro SMTP)
        # O smtplib.SMTP_SSL é frequentemente mais seguro e direto para o porto 465, mas mantive o TLS (starttls) se for o padrão (porta 587)
        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.starttls()  # Inicia TLS para segurança
            server.login(SMTP_SENDER_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        
        print(f"SUCESSO: Alerta de lead enviado para {RECEIVER_EMAIL}")

    except Exception as e:
        print(f"ERRO CRÍTICO ao enviar e-mail de alerta (SMTP/Zoho): {e}")


# --- Configuração do App ---
app = Flask(__name__)
CORS(app) 
# --- Fim da Configuração do App ---


# --- ROTAS DA LANDING PAGE (FRONTEND) ---

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a Política de Privacidade (CORREÇÃO APLICADA AQUI)
@app.route('/politica-de-privacidade.html')
def politica_de_privacidade():
    return render_template('politica-de-privacidade.html')

# Rota para a página de Obrigado (Adicionado para garantir o acesso)
@app.route('/obrigado.html')
def obrigado():
    return render_template('obrigado.html')

# Rota para a página de Cadastro (Adicionado para garantir o acesso)
@app.route('/cadastro.html')
def cadastro():
    return render_template('cadastro.html')


# ENDPOINT: Rota para buscar os Pacotes (Varredura Real com Tempo Mínimo)
@app.route('/api/pacotes', methods=['GET'])
def get_pacotes():
    
    start_time = time.time() # Marca o tempo de início da requisição
    
    try:
        # 1. Executa o Web Scraping real
        pacotes_atuais = realizar_web_scraping_da_vitrine()

        end_time = time.time() # Marca o tempo de fim da execução
        elapsed_time = end_time - start_time
        
        # 2. Garante um atraso mínimo para que o usuário veja o loading (melhor UX)
        MIN_DELAY = 2.0 # Mínimo de 2.0 segundos de espera total
        
        if elapsed_time < MIN_DELAY:
            # Pausa apenas o tempo que falta para atingir o mínimo
            time.sleep(MIN_DELAY - elapsed_time)
            
        # 3. Retorna a lista de pacotes (preenchida ou vazia)
        return jsonify(pacotes_atuais), 200

    except Exception as e:
        print(f"ERRO CRÍTICO no endpoint /api/pacotes: {e}")
        # Retorna lista vazia e status 500 para notificar o problema, mas sem quebrar o frontend.
        return jsonify({"message": "Falha na varredura. Retornando lista vazia."}), 500


# Rota para capturar o Lead (Endpoint da Automação)
@app.route('/capturar_lead', methods=['POST'])
def capturar_lead():
    data = request.json 
    
    # Variáveis de e-mail para uso na função de alerta (mesmo que o BD falhe)
    nome = data.get('nome', 'N/A')
    whatsapp = data.get('telefone', 'N/A')
    destino = data.get('pacoteSelecionado', 'N/A')

    try:
        # Mapeamento e Tratamento de Campos do Formulário
        pessoas = data.get('passageiros')
        data_viagem_input = data.get('dataViagem')
        data_viagem = data_viagem_input if data_viagem_input else None 
        
        # Campos que o novo formulário NÃO coleta (inseridos como NULL)
        email = None
        tipo_viagem = None
        orcamento = None
        
        # Conectar ao banco de dados
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        
        if db_url_corrigida:
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
            print("SUCESSO: Lead salvo no BD.")
        else:
            print("AVISO: DATABASE_URL não configurada. Lead NÃO SALVO no BD.")

        
        # --- NOVO PASSO: Dispara o Robô de Prospecção (E-mail) ---
        enviar_alerta_lead(nome, whatsapp, destino)
        
        # Retorna sucesso para o Frontend (que então abrirá o WhatsApp)
        return jsonify({'success': True, 'message': 'Lead salvo e alerta enviado!'}), 200

    except Exception as e:
        # Fluxo de Falha: Tenta enviar o alerta mesmo se o BD falhar (o Robô é a prioridade)
        print(f"ERRO DE BANCO DE DADOS/SERVIDOR: {e}")
        enviar_alerta_lead(nome, whatsapp, destino) # Tenta enviar o alerta mesmo na falha
        
        # Retorna 200 para que o frontend abra o WhatsApp e não quebre a UX
        return jsonify({'success': False, 'message': f'Erro no servidor: {str(e)}'}), 200 


# --- ROTAS DE GERENCIAMENTO ---

# Rota para a página de leads (mantida)
@app.route('/leads.html', methods=['GET'])
def leads():
    try:
        db_url_corrigida = corrigir_url_db(os.environ.get('DATABASE_URL'))
        if not db_url_corrigida:
            # Renderiza a página com uma mensagem de erro no lugar dos leads
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
        # Retorna a página com o erro para visualização
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
    # Roda com o servidor de desenvolvimento do Flask.
    # Em produção (Railway), o Gunicorn assume o controle.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
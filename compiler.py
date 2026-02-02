from flask import Flask, render_template
from flask_frozen import Freezer
import os

app = Flask(__name__)

# --- AJUSTE AQUI ---
# Alteramos de 'build' para '.' para que ele gere os arquivos na RAIZ do repositório
app.config['FREEZER_DESTINATION'] = '.' 
app.config['FREEZER_RELATIVE_URLS'] = True

freezer = Freezer(app)

@app.route('/')
def index():
    # Lógica de posts do FSR Viagens e Turismo
    posts = [
        {
            "titulo": "Guia de Fernando de Noronha", 
            "data": "2026-02-01",
            "imagem": "https://images.unsplash.com/photo-1599427303058-f06cbdf4290f?w=800",
            "resumo": "Descubra as praias mais bonitas do Brasil."
        },
        {
            "titulo": "Como planejar sua Eurotrip", 
            "data": "2026-01-25",
            "imagem": "https://images.unsplash.com/photo-1527631746610-bca00a040d60?w=800",
            "resumo": "Dicas essenciais para economizar na sua viagem à Europa."
        }
    ]
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    # Gera o site estático
    freezer.freeze()
    
    # --- NOVO: GERA O ARQUIVO CNAME AUTOMATICAMENTE NA RAIZ ---
    # Isso garante que o GitHub sempre saiba que o site é o fsr.tur.br
    with open('CNAME', 'w') as f:
        f.write('fsr.tur.br')
        
    print("Sucesso! Blog gerado na raiz do projeto com o arquivo CNAME.")

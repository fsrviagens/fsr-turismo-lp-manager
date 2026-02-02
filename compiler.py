from flask import Flask, render_template
from flask_frozen import Freezer
import os

app = Flask(__name__)

# Configurações para o GitHub Pages
# O Frozen-Flask precisa saber que o destino é a pasta 'docs' ou a raiz
app.config['FREEZER_DESTINATION'] = 'build'
app.config['FREEZER_RELATIVE_URLS'] = True

freezer = Freezer(app)

@app.route('/')
def index():
    # Aqui você mantém sua lógica de posts do FSR Viagens e Turismo
    posts = [
        {"titulo": "Guia de Fernando de Noronha", "data": "2026-02-01"},
        {"titulo": "Como planejar sua Eurotrip", "data": "2026-01-25"}
    ]
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    freezer.freeze()
    print("Sucesso! Blog gerado na pasta /build")
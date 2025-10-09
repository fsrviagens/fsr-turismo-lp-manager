# Use a imagem oficial do Python como base
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /usr/src/app

# Copie os arquivos de requisitos e instale as dependências
COPY requirements.txt ./

# O Render tem todas as dependências de compilação (libpq)
# Garanta que gunicorn, requests e beautifulsoup4 estão no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código-fonte do seu projeto para o contêiner
COPY . .

# Comando para iniciar o servidor Gunicorn no formato "Exec Form"
# Isso garante que a variável $PORT (fornecida pelo Render) seja expandida corretamente
# app:app significa: 'app.py' (módulo) : 'app' (instância Flask dentro do módulo)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]

# Nota sobre a Porta (Render):
# 1. O Render injeta a variável $PORT.
# 2. O Render geralmente exige que você use a porta 10000.
# 3. É mais seguro usar uma porta padrão (como 8000) no Dockerfile.
# 4. No Render, você configura o "Start Command" como gunicorn --bind 0.0.0.0:$PORT app:app.
# O Render NÃO usa o CMD do Dockerfile se o Start Command estiver configurado.
# Se você estiver confiando apenas no Dockerfile, e o Render não injetar $PORT na linha CMD,
# 8000 é uma porta segura para usar, e o Render mapeará para a porta 80/443 externamente.
# Vamos usar 8000 no Dockerfile por segurança e assumir que o Render cuidará do mapeamento.

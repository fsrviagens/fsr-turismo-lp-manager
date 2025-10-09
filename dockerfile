# Use a imagem oficial do Python como base
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /usr/src/app

# Copie os arquivos de requisitos e instale as dependências
COPY requirements.txt ./
# O Render tem todas as dependências de compilação (libpq) que faltavam no Termux
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código-fonte do seu projeto para o contêiner
COPY . .

# EXPOSE é opcional, mas se mantido, deve ser 0.0.0.0:$PORT.
# Melhor remover esta linha ou deixá-la genérica, mas o comando CMD é o que importa.
# EXPOSE 8000  <-- Remova esta linha ou deixe-a assim: EXPOSE $PORT

# Comando para iniciar o servidor Gunicorn
# CORREÇÃO: Usa $PORT para o Render.
CMD gunicorn --bind 0.0.0.0:$PORT app:app

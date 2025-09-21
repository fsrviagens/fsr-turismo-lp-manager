# Use a imagem oficial do Python como base
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /usr/src/app

# Copie os arquivos de requisitos e instale as dependências
# Crie um arquivo requirements.txt com as dependências do seu projeto (flask, psycopg2)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código-fonte do seu projeto para o contêiner
COPY . .

# Expõe a porta que o aplicativo irá rodar
EXPOSE 8000

# Comando para iniciar o servidor Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]

# Use a imagem oficial do Python como base (python:3.10-slim é a mais atual estável)
FROM python:3.10-slim

# Defina o diretório de trabalho
WORKDIR /usr/src/app

# Copie apenas os requisitos para aproveitar o cache do Docker
COPY requirements.txt ./

# CRÍTICO: Instala as dependências de sistema necessárias para psycopg2 (PostgreSQL)
# e pacotes de build.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Limpa o apt novamente após o pip para garantir a imagem slim
RUN apt-get autoremove -y build-essential gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia o código-fonte
COPY . .

# CRIAÇÃO DE USUÁRIO NÃO-ROOT (MELHOR PRÁTICA DE SEGURANÇA)
RUN useradd -m appuser
USER appuser

# Expor a porta 8000
EXPOSE 8000

# Comando para iniciar o Gunicorn
# Ajuste -w (workers) conforme a capacidade da sua VM (2*vCPUs + 1)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-w", "3", "app:app"]
# ----------------------------------------------------------------------
# ESTÁGIO 1: BUILDER (Compilação do psycopg2 para Python 3.13)
# ----------------------------------------------------------------------
# Alinhado com o log de erro: força o uso do Python 3.13.
FROM python:3.13-slim as builder 

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia apenas os requisitos
COPY requirements.txt ./

# CRÍTICO: Reintroduz as dependências de sistema para COMPILAÇÃO
# (necessário porque mudamos para 'psycopg2' em vez de 'psycopg2-binary').
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Instala as dependências Python (o psycopg2 será compilado aqui)
RUN pip install --no-cache-dir -r requirements.txt


# ----------------------------------------------------------------------
# ESTÁGIO 2: FINAL (Imagem de produção, limpa e segura)
# ----------------------------------------------------------------------
# Alinhado com o estágio 1.
FROM python:3.13-slim as final 

# Reinstala apenas a biblioteca de sistema necessária para a execução (runtime) do psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia os pacotes Python instalados do estágio 'builder'
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copia o código-fonte
COPY . .

# CRIAÇÃO DE USUÁRIO NÃO-ROOT
RUN useradd -m appuser
USER appuser

# Expor a porta
EXPOSE 5000

# Comando para iniciar o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "3", "app:app"]
# ----------------------------------------------------------------------
# ESTÁGIO 1: BUILDER (Compilação de dependências como psycopg2)
# ----------------------------------------------------------------------
FROM python:3.11-slim as builder

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia apenas os requisitos
COPY requirements.txt ./

# CRÍTICO: Instala as dependências de sistema necessárias para compilação (libpq-dev)
# e as ferramentas de build (build-essential, gcc).
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Instala as dependências Python (roda a compilação aqui)
RUN pip install --no-cache-dir -r requirements.txt


# ----------------------------------------------------------------------
# ESTÁGIO 2: FINAL (Imagem de produção, limpa e segura)
# ----------------------------------------------------------------------
FROM python:3.11-slim as final

# Reinstala apenas a biblioteca de sistema necessária para a execução (runtime) do psycopg2
# libpq5 é o pacote de runtime que substitui libpq-dev (pacote de desenvolvimento/build)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia os pacotes Python instalados do estágio 'builder'
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copia o código-fonte
COPY . .

# CRIAÇÃO DE USUÁRIO NÃO-ROOT (MELHOR PRÁTICA DE SEGURANÇA)
# Deve ser feito na imagem final para ter efeito
RUN useradd -m appuser
USER appuser

# Expor a porta 5000 (Padrão do Railway/ambiente de deploy e do app.py fallback)
EXPOSE 5000

# Comando para iniciar o Gunicorn
# Ajuste -w (workers) conforme a capacidade da sua VM (2*vCPUs + 1)
# CORREÇÃO: Usando a porta 5000 para ser consistente com o EXPOSE e o app.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "3", "app:app"]
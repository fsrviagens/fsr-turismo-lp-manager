# ----------------------------------------------------------------------
# ESTÁGIO 1: BUILDER (Otimizado para psycopg2-binary)
# ----------------------------------------------------------------------
# Correção: Usando python:3.11-slim para evitar a incompatibilidade do Python 3.13 
# com psycopg2, conforme detectado nos logs anteriores.
FROM python:3.11-slim as builder

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia apenas os requisitos
COPY requirements.txt ./

# OTIMIZAÇÃO CRÍTICA: Não é mais necessário instalar 'build-essential' ou 'gcc' 
# porque você está usando 'psycopg2-binary'. Apenas o 'libpq-dev' seria o necessário
# para o 'psycopg2' (não-binário), mas para o 'psycopg2-binary', 
# só precisamos do pacote de runtime (libpq5), que está no estágio 'final'.
# Deixamos este RUN limpo para a instalação do pip.
RUN pip install --no-cache-dir -r requirements.txt


# ----------------------------------------------------------------------
# ESTÁGIO 2: FINAL (Imagem de produção, limpa e segura)
# ----------------------------------------------------------------------
FROM python:3.11-slim as final

# OTIMIZAÇÃO/CRÍTICO: libpq5 é o pacote de runtime necessário para o psycopg2-binary
# funcionar. É a única dependência de sistema necessária agora.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia os pacotes Python instalados do estágio 'builder'
# Nota: O caminho /usr/local/lib/python3.11/site-packages é o correto para imagens Python oficiais.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copia o código-fonte
COPY . .

# CRIAÇÃO DE USUÁRIO NÃO-ROOT (MELHOR PRÁTICA DE SEGURANÇA)
RUN useradd -m appuser
USER appuser

# Expor a porta 5000 (Boa prática, mas a porta real é definida pelo gunicorn)
EXPOSE 5000

# Comando para iniciar o Gunicorn
# Ajuste -w (workers) conforme a capacidade da sua VM (Regra geral: 2*vCPUs + 1)
# Recomendação: Usar a variável de ambiente PORT (ex: $PORT) se o ambiente de deploy (Railway, Heroku) 
# a define, mas 0.0.0.0:5000 é um bom fallback.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "3", "app:app"]
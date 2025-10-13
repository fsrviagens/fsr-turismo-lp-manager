# ----------------------------------------------------------------------
# ESTÁGIO 1: BUILDER (Retorno à versão estável Python 3.11)
# ----------------------------------------------------------------------
# CORREÇÃO CRÍTICA: Retorna para 3.11, que é comprovadamente compatível com o psycopg2-binary.
FROM python:3.11-slim as builder 

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia apenas os requisitos
COPY requirements.txt ./

# OTIMIZAÇÃO: Não precisamos de ferramentas de compilação (build-essential, gcc)
# porque estamos usando 'psycopg2-binary' (necessário no 3.11).
RUN pip install --no-cache-dir -r requirements.txt


# ----------------------------------------------------------------------
# ESTÁGIO 2: FINAL (Imagem de produção, limpa e segura)
# ----------------------------------------------------------------------
# Alinhado com o estágio 1.
FROM python:3.11-slim as final 

# Instala apenas a biblioteca de sistema necessária para o runtime (libpq5).
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

# CRIAÇÃO DE USUÁRIO NÃO-ROOT
RUN useradd -m appuser
USER appuser

# Expor a porta
EXPOSE 5000

# Comando para iniciar o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "3", "app:app"]

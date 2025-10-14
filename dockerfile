# ----------------------------------------------------------------------
# ESTÁGIO 1: BUILDER 
# ----------------------------------------------------------------------
FROM python:3.11-slim as builder 

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia apenas os requisitos (Assumindo que requirements.txt já está corrigido com Pillow e pytesseract)
COPY requirements.txt ./

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt


# ----------------------------------------------------------------------
# ESTÁGIO 2: FINAL (Imagem de produção, limpa e segura)
# ----------------------------------------------------------------------
FROM python:3.11-slim as final 

# Instala as bibliotecas de sistema necessárias para o runtime:
# 1. libpq5 (para psycopg2-binary)
# 2. tesseract-ocr (Motor de Reconhecimento Óptico de Caracteres - OCR)
# 3. tesseract-ocr-por (Dados de idioma Português para o OCR)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    tesseract-ocr \
    tesseract-ocr-por && \
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

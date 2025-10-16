FROM python:3.11-slim as builder 

WORKDIR /usr/src/app

COPY requirements.txt ./

# Instala as dependências Python (agora sem pytesseract, requests, etc.)
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim as final 

# Instala apenas o libpq5 (necessário para psycopg2-binary, o DB de Leads)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY . .

RUN useradd -m appuser
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "3", "app:app"]
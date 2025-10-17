# agencia_app/core/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (apenas no ambiente local)
load_dotenv() 

# ... (Outras configurações)

# --------------------------
# CONFIGURAÇÃO DE SEGURANÇA
# --------------------------

SECRET_KEY = os.getenv('SECRET_KEY', 'default-django-secret-key-para-local')

# Em produção, o Railway pode definir ALLOWED_HOSTS.
# Para local, você pode adicionar 'localhost' e '127.0.0.1'.
ALLOWED_HOSTS = ['*'] # Permite todas as conexões (ajustar em produção)

# --------------------------
# CONFIGURAÇÃO DE APLICAÇÕES
# --------------------------

INSTALLED_APPS = [
    # ... apps do Django
    'agencia_app', # O nome do seu app
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    # Apps de Terceiros que você instalou:
    'whitenoise.runserver_nostatic', # Para servir estáticos em dev
    'corsheaders', # Para o django-cors-headers
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Adicionar o Whitenoise logo abaixo do SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    # Adicionar o CORS Headers
    'corsheaders.middleware.CorsMiddleware', 
    # ... (outros middlewares)
]

# --------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS (SUPABASE)
# --------------------------

# Conecta ao DATABASE_URL fornecido pelo Railway/Supabase.
# Se a variável DATABASE_URL não existir (ambiente local sem .env),
# ele usará o SQLite padrão.
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600 # Configuração opcional para performance
    )
}

# --------------------------
# CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS
# --------------------------

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Onde o Whitenoise procurará os arquivos em produção
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

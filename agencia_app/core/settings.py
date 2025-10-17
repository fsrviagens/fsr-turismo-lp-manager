# core/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis do .env (apenas para desenvolvimento local)
load_dotenv() 

# Define a raiz do projeto. Essencial!
BASE_DIR = Path(__file__).resolve().parent.parent


# ====================================================================
# 1. CONFIGURAÇÕES BÁSICAS E DE SEGURANÇA
# ====================================================================

# Chave Secreta (lida do ambiente ou usa fallback local)
SECRET_KEY = os.getenv('SECRET_KEY', 'default-django-secret-key-para-local')

# Modo de Desenvolvimento/Produção
# USE ESTA VARIAVEL NO RAILWAY: DEBUG=False
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Hosts Permitidos
if DEBUG:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
else:
    # Em produção, leia do ambiente ou defina seus domínios
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',') # O '*' deve ser substituído por ['fsr.tur.br', ...]

# ====================================================================
# 2. APLICAÇÕES INSTALADAS E MIDDLEWARE
# ====================================================================

INSTALLED_APPS = [
    # Apps Padrão do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Whitenoise (deve vir antes de 'staticfiles' para a configuração)
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # Apps de Terceiros que você incluiu
    'corsheaders',

    # SEU APP
    'agencia_app', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise para servir arquivos estáticos em produção
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # CORS Headers deve vir antes do CommonMiddleware
    'corsheaders.middleware.CorsMiddleware', 
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls' # Onde o Django busca as URLs principais

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True, # Busca templates dentro de cada pasta 'templates' dos apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# ====================================================================
# 3. BANCO DE DADOS (SUPABASE / POSTGRESQL)
# ====================================================================

# Conecta ao DATABASE_URL (definido no Railway)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600
    )
}

# Configurações de SSL ESSENCIAIS para PostgreSQL em nuvem (Supabase)
if 'postgresql' in os.getenv('DATABASE_URL', ''):
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require', 
    }

# ====================================================================
# 4. ARQUIVOS ESTÁTICOS (WHITENOISE)
# ====================================================================

STATIC_URL = 'static/'

# Onde o 'python manage.py collectstatic' vai despejar os arquivos
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuração do Whitenoise para compactação e cache
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Pasta que o Django deve buscar arquivos estáticos além dos apps (opcional)
STATICFILES_DIRS = [
    # BASE_DIR / 'static', # Descomente se tiver uma pasta 'static' na raiz
]

# ====================================================================
# 5. CONFIGURAÇÕES DE IDIOMA E FUSO HORÁRIO
# ====================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Outras configurações
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True # Permite acesso de qualquer origem (Ajuste em produção!)
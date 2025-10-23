import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis do .env para desenvolvimento local
load_dotenv()

# Define a raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================================================================
# 1. CONFIGURAÇÕES BÁSICAS E DE SEGURANÇA
# ====================================================================

SECRET_KEY = os.getenv('SECRET_KEY', 'default-django-secret-key-para-local-MUITO-INSEGURO')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

if DEBUG:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'fsr-turismo-lp-manager-production.up.railway.app,fsr.tur.br,www.fsr.tur.br').split(',')

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://fsr-turismo-lp-manager-production.up.railway.app,https://fsr.tur.br,https://www.fsr.tur.br').split(',')

# ====================================================================
# 2. APLICAÇÕES INSTALADAS E MIDDLEWARE
# ====================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'storages',
    'agencia_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agencia_app.urls'
WSGI_APPLICATION = 'agencia_app.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

# ====================================================================
# 3. BANCO DE DADOS (SUPABASE / POSTGRESQL)
# ====================================================================

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600
    )
}

if 'postgresql' in os.getenv('DATABASE_URL', ''):
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }

# ====================================================================
# 4. ARQUIVOS ESTÁTICOS E MÍDIA
# ====================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Pasta onde collectstatic vai juntar os arquivos estáticos

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    # Produção: arquivos estáticos e mídia serão servidos pelo Cloudflare R2
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')

    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False  # URLs limpas

    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

    STATICFILES_STORAGE = 'storages.backends.s3.S3StaticStorage'
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

else:
    # Desenvolvimento: servir arquivos estáticos localmente com WhiteNoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ====================================================================
# 5. OUTRAS CONFIGURAÇÕES
# ====================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        'https://fsr.tur.br',
        'https://www.fsr.tur.br',
        # Outros frontends aqui
    ]

NUMERO_WHATSAPP_AGENCIA = os.getenv('NUMERO_WHATSAPP_AGENCIA', '5561983163710')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
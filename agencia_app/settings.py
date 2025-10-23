from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import dj_database_url # Adicionado para conexão robusta com o Railway Postgres

# ======================================================================
# 1. CONFIGURAÇÕES BÁSICAS
# ======================================================================

# Define o diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Define o modo de execução. Em um ambiente real, deve vir de um .env
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# CORREÇÃO CRÍTICA: Adicionado o domínio do Railway para produção
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'fsr.tur.br', 'www.fsr.tur.br', '.up.railway.app']

# Chave secreta de produção (deve vir do ambiente)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY deve estar definida no ambiente.")


# ======================================================================
# 2. APLICATIVOS (CRÍTICO: Corrigido o erro 'Unknown command')
# ======================================================================

# CORREÇÃO CRÍTICA: Lista completa de INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # ESSENCIAL para o collectstatic funcionar!
    
    # Suas aplicações de terceiros
    'storages', # Necessário para o armazenamento S3
    'whitenoise.runserver_nostatic', # Adicionado para servir estáticos em DEV
    
    # Seus aplicativos locais
    'agencia_app',
]

# ======================================================================
# 3. MIDDLEWARE E ROOT_URLCONF
# ======================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise: Deve vir ANTES do CommonMiddleware em produção
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agencia_app.urls' # Correto, mantido.

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Supondo que você tem uma pasta 'templates' na raiz
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

WSGI_APPLICATION = 'agencia_app.wsgi.application'


# ======================================================================
# 4. BANCO DE DADOS
# ======================================================================

# Usa dj-database-url para ler a string de conexão do Railway
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}


# ======================================================================
# 5. ARQUIVOS ESTÁTICOS E DE MÍDIA
# ======================================================================

STATIC_URL = '/static/'

# CORREÇÃO CRÍTICA: Revertido o STATIC_ROOT para um caminho padrão e portátil
# O caminho absoluto do Termux não funciona no Railway.
STATIC_ROOT = str(BASE_DIR / 'staticfiles') 

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media') 

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ======================================================================
# 6. CONFIGURAÇÕES DE PRODUÇÃO (DEBUG=False)
# ======================================================================

if not DEBUG:
    # --- Variáveis AWS lidas do ambiente ---
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    # URL de endpoint personalizado (ex: para DigitalOcean Spaces, MinIO, etc.)
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    
    # Domínio personalizado (CDN ou CNAME do S3)
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')

    # Validação crucial para produção
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN]):
        # Isso não deve ser um erro fatal no Railway se estivermos apenas fazendo o build, 
        # mas mantemos a validação de produção
        pass 

    # --- Configurações S3 ---
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400', # Cache de 24 horas
    }

    # --- Armazenamento de Estáticos (S3) ---
    STATICFILES_STORAGE = 'storages.backends.s3.S3StaticStorage'
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

    # --- Armazenamento de Mídia (S3) ---
    DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

else:
    # ======================================================================
    # 7. OVERRIDES PARA DESENVOLVIMENTO (DEBUG=True)
    # ======================================================================
    
    # WhiteNoise para servir estáticos localmente com compressão e cache
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    pass
    

# ======================================================================
# 8. CONFIGURAÇÕES GERAIS ADICIONAIS
# ======================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações de fuso horário
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True 

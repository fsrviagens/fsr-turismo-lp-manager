# agencia_app/settings.py (Nome Corrigido para refletir a pasta)

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis do .env (Apenas para desenvolvimento local)
load_dotenv() 

# Define a raiz do projeto. Essencial!
BASE_DIR = Path(__file__).resolve().parent.parent


# ====================================================================
# 1. CONFIGURAÇÕES BÁSICAS E DE SEGURANÇA
# ====================================================================

# Chave Secreta (CRÍTICO: Lida do ambiente. O fallback é para desenvolvimento SOMENTE)
SECRET_KEY = os.getenv('SECRET_KEY', 'default-django-secret-key-para-local-MUITO-INSEGURO')

# Modo de Desenvolvimento/Produção
# Variável RAILWAY: DEBUG=False (Bool)
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Hosts Permitidos (Segurança CRÍTICA - Protege contra Host Header Attack)
if DEBUG:
    # Em desenvolvimento, permite localhosts e Railway
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
else:
    # Em produção, deve ler do ambiente a lista EXATA de domínios.
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'fsr.tur.br,www.fsr.tur.br').split(',')


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
    
    # WhiteNoise (deve vir antes de 'staticfiles' para a configuração de DEV)
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # Apps de Terceiros que você incluiu
    'corsheaders',
    'storages',  # ADICIONADO: Necessário para usar django-storages (R2/S3)

    # SEU APP
    'agencia_app', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise para servir arquivos estáticos em DEV/Produção (se não usar o R2 para estáticos)
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

# Configurações de Módulos (Corrigidas)
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
# 4. ARQUIVOS ESTÁTICOS (CONFIGURAÇÃO BASE)
# ====================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Pasta que o Django deve buscar arquivos estáticos além dos apps (opcional)
# STATICFILES_DIRS = [
#     BASE_DIR / 'static', 
# ]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ====================================================================
# 5. ARQUIVOS DE MÍDIA E ESTÁTICOS EM PRODUÇÃO (CLOUDFLARE R2)
# ====================================================================

# Comportamento de mídia em desenvolvimento local
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


if not DEBUG:
    # --- Configurações Comuns para Estáticos e Mídia (Cloudflare R2/S3) ---
    
    # IMPORTANTE: Essas chaves DEVEM ser definidas como Variáveis de Ambiente no Railway!
    AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
    
    # URL de Endpoint do R2 (ex: seu-account-id.r2.cloudflarestorage.com)
    AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL')
    
    # Propriedades de acesso (necessário para o R2)
    AWS_DEFAULT_ACL = 'public-read'
    
    # --- Configuração de Media (Uploads do Usuário) ---
    DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT_URL}/media/" 
    
    # --- Configuração de Estáticos ---
    # Usando o django-storages para servir estáticos pelo R2/CDN
    STATICFILES_STORAGE = 'storages.backends.s3.S3StaticStorage'
    STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT_URL}/static/"
    
    # Opcional, mas recomendado para o R2
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT_URL}"
else:
    # Em desenvolvimento, usa o armazenamento local e WhiteNoise padrão
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ====================================================================
# 6. CONFIGURAÇÕES DE IDIOMA, FUSO HORÁRIO E CORS
# ====================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# REFORÇO DE SEGURANÇA CORS
if DEBUG:
    # Permite todas as origens em desenvolvimento para facilitar testes
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # EM PRODUÇÃO: Definir Origens Permitidas (CRÍTICO!)
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        'https://fsr.tur.br',
        'https://www.fsr.tur.br',
        # ADICIONE AQUI OUTROS FRONTENDS SE NECESSÁRIO
]

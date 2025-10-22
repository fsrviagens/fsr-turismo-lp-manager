# agencia_app/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis do .env (Apenas para desenvolvimento local)
# Útil para carregar a SECRET_KEY, DEBUG, e as chaves R2 localmente.
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
# Converte a string do ambiente para booleano
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

# Hosts Permitidos (Segurança CRÍTICA - Protege contra Host Header Attack)
if DEBUG:
    # Em desenvolvimento, permite localhosts
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
else:
    # Em produção, deve ler do ambiente a lista EXATA de domínios.
    # Garanta que a variável ALLOWED_HOSTS no Railway esteja configurada como 'dominio1,dominio2'
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'fsr-turismo-lp-manager-production.up.railway.app,fsr.tur.br,www.fsr.tur.br').split(',')


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
    
    # IMPORTANTE: django.contrib.staticfiles deve vir antes
    'django.contrib.staticfiles',

    # Apps de Terceiros que você incluiu
    'corsheaders',
    'storages',  # Necessário para usar django-storages (R2/S3)

    # SEU APP
    'agencia_app', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise: Apenas para arquivos estáticos locais em DEV, ou como fallback
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

# Configurações de Módulos
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

# Configurações básicas que são a base para o uso em DEBUG=True
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ====================================================================
# 5. ARQUIVOS DE MÍDIA E ESTÁTICOS EM PRODUÇÃO (CLOUDFLARE R2)
# ====================================================================

# Comportamento de mídia em desenvolvimento local
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


if not DEBUG:
    # --- Configurações Comuns para Estáticos e Mídia (Cloudflare R2/S3) ---
    
    # 1. Lendo as chaves AWS/S3 (nomes padronizados para django-storages)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    # 2. URL de Endpoint do R2 (CRÍTICO para R2)
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    
    # 3. Custom Domain (URL pública para o navegador)
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    
    # Propriedades de acesso
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False # Desativa assinatura de URL (URLs limpas)
    
    # Opcional: Configurações de Cache 
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400', # Cache por 1 dia
    }
    
    # --- Configuração de Media (Uploads do Usuário) ---
    DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
    
    # Usando o Custom Domain para a URL pública (Ex: https://dominio.com/media/...)
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/" 
    
    # --- Configuração de Estáticos ---
    STATICFILES_STORAGE = 'storages.backends.s3.S3StaticStorage'
    
    # Usando o Custom Domain para a URL pública (Ex: https://dominio.com/static/...)
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    
    # Note: O comando `collectstatic` agora enviará os arquivos para o R2.

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


# ====================================================================
# 7. VARIÁVEIS CUSTOMIZADAS E DA APLICAÇÃO (Ajuste Integrado)
# ====================================================================

# Número de WhatsApp da Agência (Usado em views.py para redirecionamento)
# Lendo do ambiente. O fallback garante que o acesso via settings.NUMERO_WHATSAPP_AGENCIA 
# não cause um erro de atributo.
NUMERO_WHATSAPP_AGENCIA = os.getenv('NUMERO_WHATSAPP_AGENCIA', '5561983163710') 

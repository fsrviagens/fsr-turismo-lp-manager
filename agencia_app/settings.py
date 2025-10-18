# agencia_app/settings.py (Nome Corrigido para refletir a pasta)

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis do .env (Apenas para desenvolvimento local e chaves que não são secrets no Railway)
load_dotenv() 

# Define a raiz do projeto. Essencial!
BASE_DIR = Path(__file__).resolve().parent.parent


# ====================================================================
# 1. CONFIGURAÇÕES BÁSICAS E DE SEGURANÇA
# ====================================================================

# Chave Secreta (CRÍTICO: Lida do ambiente. O fallback local é SOMENTE para desenvolvimento)
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
    # Ex: ALLOWED_HOSTS = fsr.tur.br,www.fsr.tur.br,8w3neyqk.up.railway.app
    # O fallback é uma vulnerabilidade, mas necessário se a variável não estiver definida.
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
    
    # WhiteNoise (deve vir antes de 'staticfiles' para a configuração)
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # Apps de Terceiros que você incluiu
    'corsheaders',
    # ADICIONE AQUI: O Backend de Storage, se estiver usando S3 ou R2
    # 'storages', 

    # SEU APP
    'agencia_app', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise para servir arquivos estáticos em produção (ADICIONADO)
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

# CORREÇÃO CRÍTICA: Módulos devem apontar para 'agencia_app'
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

# Configurações de SSL ESSENCIAIS para PostgreSQL em nuvem
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
    # BASE_DIR / 'static', 
]

# ====================================================================
# 5. ARQUIVOS DE MÍDIA (UPLOAD DE USUÁRIOS) - ESTRATÉGIA SÊNIOR
# ====================================================================

if not DEBUG:
    # Se em produção, forçamos o uso de armazenamento externo para PERSISTÊNCIA.
    
    # URL de Mídia (ajuste o nome do bucket e a região)
    # Exemplo S3/AWS:
    # MEDIA_URL = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/media/" 
    
    # Backend de Storage. Se não for S3, mude para o seu provedor.
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'
    
    # As seguintes chaves DEVEM ser definidas como Variáveis de Ambiente no Railway!
    # AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    # AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

    # SE VOCÊ NÃO TEM UPLOADS DE USUÁRIOS, PODE MANTER ESSA SEÇÃO COMENTADA.
    pass
else:
    # Comportamento de mídia em desenvolvimento local
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


# ====================================================================
# 6. CONFIGURAÇÕES DE IDIOMA, FUSO HORÁRIO E CORS
# ====================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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

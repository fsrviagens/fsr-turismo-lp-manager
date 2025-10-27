# agencia_app/settings.py

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
# IMPORTANTE: Usamos o 'decouple' para ler o .env em desenvolvimento e variáveis do SO em produção
from decouple import config 

# ======================================================================
# 1. CONFIGURAÇÕES BÁSICAS
# ======================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Usa 'decouple' para ler a variável de ambiente DEBUG
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

# Lendo a SECRET_KEY de forma segura
SECRET_KEY = config('DJANGO_SECRET_KEY')
if not SECRET_KEY and not DEBUG:
    # Apenas lança erro se não estivermos em DEBUG (produção)
    raise ImproperlyConfigured("DJANGO_SECRET_KEY deve estar definida no ambiente de Produção.")


# CORREÇÃO CRÍTICA: Ajustado ALLOWED_HOSTS para ler os valores de forma segura (usando config)
# Em produção, o Railway fornecerá o domínio.
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='127.0.0.1,localhost', 
    cast=lambda v: [s.strip() for s in v.split(',')] # Converte string CSV em lista
)
# A lista de ALLOWED_HOSTS em produção deve ser: ['seu-subdominio.up.railway.app', 'seusite.com', 'www.seusite.com']


# ----------------------------------------------------------------------
# 2. APLICAÇÕES
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', 
    
    # Suas aplicações de terceiros
    'storages', 
    'whitenoise.runserver_nostatic', 
    
    # Seus aplicativos locais
    'agencia_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ----------------------------------------------------------------------
# 3. TEMPLATES E URLS (CORRIGIDO PARA: admin.E403, ModuleNotFoundError)
# ----------------------------------------------------------------------

# ESSENCIAL: Adicionado para o Admin e para a renderização de templates (admin.E403)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS: Adicione aqui a pasta global de templates, se existir. Ex: [BASE_DIR / 'templates']
        'DIRS': [], 
        'APP_DIRS': True, # Ponto chave: Permite que as apps (como admin) carreguem templates de suas pastas
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

# CORREÇÃO CRÍTICA: Nome do módulo principal definido como 'agencia_app'
# O nome 'agencia_app' é usado porque é a pasta que contém o urls.py e wsgi.py
ROOT_URLCONF = 'agencia_app.urls' 
WSGI_APPLICATION = 'agencia_app.wsgi.application'

# ----------------------------------------------------------------------
# 4. BANCO DE DADOS
# ----------------------------------------------------------------------

# Usa 'config' para ler a DATABASE_URL de forma mais limpa
DATABASE_URL = config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600
    )
}

# ----------------------------------------------------------------------
# 5. VALIDADORES DE PASSWORD
# ----------------------------------------------------------------------
# Requerido pelo Django
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ----------------------------------------------------------------------
# 6. INTERNACIONALIZAÇÃO
# ----------------------------------------------------------------------

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# ----------------------------------------------------------------------
# 7. CONFIGURAÇÕES ESTÁTICAS E DE MEDIA (Exemplo)
# ----------------------------------------------------------------------
# (O código da Seção 7 do seu settings.py atual, sobre staticfiles/media, foi mantido)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# 8. CONFIGURAÇÕES GERAIS ADICIONAIS (CORRIGIDO PARA: models.W042)
# ----------------------------------------------------------------------

# CORREÇÃO: Adicionado para resolver o warning (models.W042).
# Define o tipo de campo automático para chaves primárias dos modelos.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ----------------------------------------------------------------------
# 9. VARIÁVEIS DE APLICAÇÃO PERSONALIZADAS (CRÍTICO PARA A VIEW)
# ----------------------------------------------------------------------

# Variável usada no views.py para o redirecionamento do WhatsApp
NUMERO_WHATSAPP_AGENCIA = config('NUMERO_WHATSAPP_AGENCIA', default='5561983163710') 

# settings.py

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured

# ======================================================================
# 1. CONFIGURAÇÕES BÁSICAS
# ======================================================================

# Define o diretório base do projeto
# CORREÇÃO: Usamos a forma padrão, mas confiamos no STATIC_ROOT para a correção.
BASE_DIR = Path(__file__).resolve().parent.parent

# Define o modo de execução. Em um ambiente real, deve vir de um .env
# Usando 'True' como fallback para desenvolvimento
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Necessário para DEBUG=False. Em produção, substitua pelo seu domínio/IP
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'fsr.tur.br', 'www.fsr.tur.br']

# ======================================================================
# 2. ARQUIVOS ESTÁTICOS E DE MÍDIA (CONFIGURAÇÕES LOCAIS/DEFAULT)
# ======================================================================

# STATIC_ROOT deve ser definido incondicionalmente para que o collectstatic funcione.
STATIC_URL = '/static/'

# === SOLUÇÃO APLICADA PARA O ERRO NO TERMUX ===
# Usamos o caminho ABSOLUTO para contornar a falha na resolução do BASE_DIR no Termux.
# ESTA LINHA DEVE SER REVERTIDA PARA str(BASE_DIR / 'staticfiles') ao sair do Termux.
STATIC_ROOT = '/data/data/com.termux/files/home/staticfiles'
# Se o seu projeto estiver em uma subpasta (ex: /home/meu_projeto/), use:
# STATIC_ROOT = '/data/data/com.termux/files/home/meu_projeto/staticfiles'
# ==============================================

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media') # Mantemos MEDIA_ROOT dinâmica.

# Lista de diretórios que o collectstatic deve procurar por arquivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ======================================================================
# 3. OVERRIDES PARA PRODUÇÃO (DEBUG=False)
# ======================================================================

if not DEBUG:
    # --- Variáveis AWS lidas do ambiente (necessárias em produção) ---
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    # URL de endpoint personalizado (ex: para DigitalOcean Spaces, MinIO, etc.)
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    
    # Domínio personalizado (CDN ou CNAME do S3)
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')

    # Validação crucial para produção
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN]):
        raise ImproperlyConfigured("Variáveis AWS_S3 (access key, secret key, bucket name, custom domain) devem estar definidas em produção.")

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
    # 4. OVERRIDES PARA DESENVOLVIMENTO (DEBUG=True)
    # ======================================================================
    
    # Usa WhiteNoise para servir estáticos localmente com compressão e cache
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Se você não estiver usando o dj-database-url, é comum usar SQLite em dev
    # DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
    pass


# ======================================================================
# 5. RESTANTE DO settings.py (Adicione aqui suas apps, templates, middleware, etc.)
# ======================================================================

# **********************************************************************
# CORREÇÃO PARA O ERRO 'AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF''
# Baseado na estrutura: o arquivo urls.py está dentro da pasta agencia_app.
# **********************************************************************
**ROOT_URLCONF = 'agencia_app.urls'** # Exemplo:
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     # ...
#     'storages', # Necessário para o armazenamento S3
#     # ...
# ]
# ...

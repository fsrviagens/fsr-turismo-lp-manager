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


# (Restante dos INSTALLED_APPS e MIDDLEWARE do seu arquivo atual...)
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
# ... (o restante das configurações TEMPLATES, WSGI_APPLICATION, etc. é mantido)


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
# 8. CONFIGURAÇÕES GERAIS ADICIONAIS
# ----------------------------------------------------------------------

# ... (outras configurações gerais, como DEFAULT_AUTO_FIELD e TIME_ZONE)

# ======================================================================
# 9. VARIÁVEIS DE APLICAÇÃO PERSONALIZADAS (CRÍTICO PARA A VIEW)
# ======================================================================

# Variável usada no views.py para o redirecionamento do WhatsApp
NUMERO_WHATSAPP_AGENCIA = config('NUMERO_WHATSAPP_AGENCIA', default='5561983163710') 

# ----------------------------------------------------------------------
# (Todo o código da Seção 5, 6 e 7 do seu settings.py atual é mantido aqui)
# ----------------------------------------------------------------------

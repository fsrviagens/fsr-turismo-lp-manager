"""
WSGI config for fsr-turismo-lp-manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# A CORREÇÃO ESTÁ AQUI: O módulo de configurações deve ser 'agencia_app.settings'
# Específica onde o Django deve procurar o settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agencia_app.settings')

application = get_wsgi_application()

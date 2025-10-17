# agencia_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URL principal da Landing Page (por exemplo: http://fsr.tur.br/)
    path('', views.landing_page, name='landing_page'),
    
    # URL para onde o formulário será submetido (POST)
    path('capturar/', views.capturar_lead, name='capturar_lead'),
]

# Documentação:
# - path('', ...): Liga a raiz do aplicativo (app) à view que exibe o CMS.
# - path('capturar/', ...): Liga o caminho de submissão do formulário à view que salva o Lead.
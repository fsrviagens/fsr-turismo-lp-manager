# agencia_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URL principal da Landing Page (por exemplo: http://fsr.tur.br/)
    path('', views.landing_page, name='landing_page'),
    
    # URL para onde o formulário será submetido (por exemplo: http://fsr.tur.br/capturar/)
    path('capturar/', views.capturar_lead, name='capturar_lead'),
]

# Documentação:
# - path('', ...): Define o caminho da URL. O vazio '' significa a raiz do site.
# - name='...': Dá um nome para a URL, o que permite usarmos 'reverse('nome')' em outras partes do código.
# - views.landing_page: Liga esta URL à função 'landing_page' dentro de views.py.
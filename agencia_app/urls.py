# agencia_app/urls.py (ÚNICO ARQUIVO DE ROTAS)

from django.contrib import admin
from django.urls import path, include
from . import views # Importa as views do aplicativo

urlpatterns = [
    # 1. Rota OBRIGATÓRIA para a área de Administração do Django
    path('admin/', admin.site.urls),
    
    # 2. Rotas do Aplicativo (Landing Page e Captura)
    # Como este é o Root URLconf, não usamos 'include', mapeamos diretamente:
    path('', views.landing_page, name='landing_page'),
    path('capturar/', views.capturar_lead, name='capturar_lead'),
]

from django.urls import path
from . import views

# Define o namespace do App
app_name = 'agencia_app'

urlpatterns = [
    # Rota principal (fsr.tur.br/)
    path('', views.landing_page, name='landing_page'),

    # Rota para processar o formulário (fsr.tur.br/capturar-lead/)
    path('capturar-lead/', views.capturar_lead, name='capturar_lead'),
]

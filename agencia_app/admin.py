# agencia_app/admin.py

from django.contrib import admin
from .models import Lead

# Customiza como o modelo Lead será exibido no painel administrativo
class LeadAdmin(admin.ModelAdmin):
    """
    Configuração de exibição do modelo Lead no Admin do Django.
    """
    # Campos que serão exibidos na lista de Leads
    list_display = ('nome', 'email', 'telefone', 'data_cadastro', 'origem')
    
    # Campos pelos quais você pode pesquisar
    search_fields = ('nome', 'email', 'telefone')
    
    # Filtros laterais (excelente para classificar por origem, por exemplo)
    list_filter = ('origem', 'data_cadastro')
    
    # Torna a data de cadastro um campo somente leitura
    readonly_fields = ('data_cadastro',)

# Registra o modelo Lead com a nossa customização
admin.site.register(Lead, LeadAdmin)

# Documentação:
# - admin.site.register(): Função para incluir o modelo na área administrativa.
# - list_display: Uma tupla de nomes de campo a serem exibidos como colunas na página de lista de objetos.
# - search_fields: Uma tupla de nomes de campo que serão pesquisados quando alguém usar a barra de pesquisa.
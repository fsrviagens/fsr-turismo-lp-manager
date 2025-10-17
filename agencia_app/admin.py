# agencia_app/admin.py

from django.contrib import admin
from .models import Lead, ConfiguracaoLandingPage # Importamos o novo modelo

# ====================================================================
# 1. ADMIN PARA LEADS (Gerenciamento de Leads)
# ====================================================================

class LeadAdmin(admin.ModelAdmin):
    """
    Configuração de exibição e gestão do modelo Lead.
    """
    # Inclui o novo campo 'destino_interesse' na lista e pesquisa.
    list_display = (
        'nome', 
        'email', 
        'telefone', 
        'destino_interesse', # <-- NOVO
        'origem', 
        'data_cadastro'
    )
    
    search_fields = ('nome', 'email', 'telefone', 'destino_interesse') # <-- NOVO
    
    list_filter = ('origem', 'destino_interesse', 'data_cadastro') # <-- NOVO
    
    readonly_fields = ('data_cadastro',)

# Registra o modelo Lead
admin.site.register(Lead, LeadAdmin)


# ====================================================================
# 2. ADMIN PARA CMS (Configuração da Landing Page)
# ====================================================================

class ConfiguracaoLandingPageAdmin(admin.ModelAdmin):
    """
    Configuração para o modelo CMS. Força a existência de apenas um registro.
    """
    # Agrupa os campos para uma visualização mais organizada.
    fieldsets = (
        ('Informações da Agência', {
            'fields': ('nome_agencia', 'logo_url'),
            'description': 'Informações básicas da agência para cabeçalho e rodapé.',
        }),
        ('Seção de Destaque (Hero)', {
            'fields': ('titulo_principal', 'subtitulo_oferta', 'imagem_url'),
            'description': 'Textos e imagem principal da Landing Page.',
        }),
        ('Detalhes da Oferta', {
            'fields': ('descricao_oferta', 'valor_oferta', 'parcelamento_max'),
            'description': 'Conteúdo da seção principal e dados financeiros.',
        }),
    )

    # Função para desabilitar o botão de "Adicionar" se já houver um registro
    def has_add_permission(self, request):
        # Permite adicionar se não houver nenhum registro.
        return not ConfiguracaoLandingPage.objects.exists()
    
    # Opcional: Redireciona para a página de edição em vez da lista, 
    # se só houver um registro (ideal para CMS de página única).
    def changelist_view(self, request, extra_context=None):
        if ConfiguracaoLandingPage.objects.count() == 1:
            obj = ConfiguracaoLandingPage.objects.get()
            return self.change_view(request, str(obj.id))
        return super().changelist_view(request, extra_context)


# Registra o modelo de Configuração do CMS
admin.site.register(ConfiguracaoLandingPage, ConfiguracaoLandingPageAdmin)

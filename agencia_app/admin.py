# agencia_app/admin.py

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from .models import Lead, ConfiguracaoLandingPage # Importamos os modelos

# ====================================================================
# 1. ADMIN PARA LEADS (Gerenciamento de Leads)
# ====================================================================

class LeadAdmin(admin.ModelAdmin):
    """
    Configuração de exibição e gestão do modelo Lead.
    """
    list_display = (
        'nome', 
        'email', 
        'telefone', 
        'destino_interesse',
        'budget_disponivel', # Adicionado para visualização rápida
        'previsao_data',     # Adicionado para visualização rápida
        'origem', 
        'data_cadastro'
    )
    
    search_fields = ('nome', 'email', 'telefone', 'destino_interesse')
    
    # Inclusão dos campos de Choices para facilitar a segmentação de vendas
    list_filter = (
        'origem', 
        'destino_interesse',
        'budget_disponivel',  # Filtro pelos Choices (R$5k-10k, etc.)
        'previsao_data',      # Filtro pelos Choices (3M, 6M, etc.)
        'data_cadastro'
    ) 
    
    readonly_fields = ('data_cadastro',)

# Registra o modelo Lead
admin.site.register(Lead, LeadAdmin)


# ====================================================================
# 2. ADMIN PARA CMS (Configuração da Landing Page)
# ====================================================================

class ConfiguracaoLandingPageAdmin(admin.ModelAdmin):
    """
    Configuração para o modelo CMS. Força a existência de apenas um registro.
    Implementa a lógica Singleton na interface Admin.
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

    # Impede que o usuário clique em "Adicionar" se já houver um registro
    def has_add_permission(self, request):
        return not ConfiguracaoLandingPage.objects.exists()
    
    # Redireciona o usuário da lista para a página de edição do único item existente.
    def changelist_view(self, request, extra_context=None):
        if ConfiguracaoLandingPage.objects.count() == 1:
            obj = ConfiguracaoLandingPage.objects.get()
            return redirect('admin:%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name), obj.id)
        # Se 0 ou mais de 1 (erro) registro, mostra a lista/tela padrão.
        return super().changelist_view(request, extra_context)


# Registra o modelo de Configuração do CMS
admin.site.register(ConfiguracaoLandingPage, ConfiguracaoLandingPageAdmin)

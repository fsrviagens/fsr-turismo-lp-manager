# agencia_app/admin.py

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from .models import Lead, ConfiguracaoLandingPage # Importamos os modelos

# ===================================================================
# 1. ADMIN PARA LEADS (Gerenciamento de Leads)
# ===================================================================

class LeadAdmin(admin.ModelAdmin):
    # ... (Seu código list_display, search_fields está OK) ...
    list_display = (
        'nome', 
        'email', 
        'telefone', 
        'destino_interesse',
        'budget_disponivel', 
        'previsao_data',     
        'origem', 
        'data_cadastro'
    )
    
    search_fields = ('nome', 'email', 'telefone', 'destino_interesse')
    
    # CORREÇÃO/AJUSTE: List_filter para usar os campos de Choices
    list_filter = (
        'origem', 
        'destino_interesse',
        'budget_disponivel',  # Filtro pelos Choices (R$5k-10k, etc.)
        'previsao_data',      # Filtro pelos Choices (3M, 6M, etc.)
        'data_cadastro'
    ) 
    
    readonly_fields = ('data_cadastro', 'origem') # Adicionando 'origem' como readonly
    ordering = ('-data_cadastro',) # Leads mais recentes primeiro

admin.site.register(Lead, LeadAdmin)


# ===================================================================
# 2. ADMIN PARA CMS (Configuração da Landing Page)
# ===================================================================

class ConfiguracaoLandingPageAdmin(admin.ModelAdmin):
    # ... (Seu código fieldsets está OK) ...
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
            'fields': ('descricao_oferta', 'parcelamento_detalhe', 'valor_oferta', 'parcelamento_max'),
            'description': 'Conteúdo da seção principal e dados financeiros.',
        }),
    )

    # CORREÇÃO: Impede que o usuário clique em "Adicionar" (Reforça a regra Singleton)
    def has_add_permission(self, request):
        return not ConfiguracaoLandingPage.objects.exists()
    
    # CORREÇÃO: Redireciona o usuário para a página de edição se já existir
    def changelist_view(self, request, extra_context=None):
        if ConfiguracaoLandingPage.objects.count() == 1:
            obj = ConfiguracaoLandingPage.objects.get()
            return redirect('admin:%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name), obj.id)
        return super().changelist_view(request, extra_context)

admin.site.register(ConfiguracaoLandingPage, ConfiguracaoLandingPageAdmin)

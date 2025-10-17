from django.contrib import admin
from .models import Lead, ConteudoLandingPage

# ==============================================================================
# Customização para o Lead (melhor visualização)
# ==============================================================================
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista de Leads
    list_display = ('nome', 'email', 'telefone', 'destino_interesse', 'data_captura', 'foi_contatado')

    # Campos para filtro rápido
    list_filter = ('foi_contatado', 'data_captura')

    # Campos de busca
    search_fields = ('nome', 'email', 'telefone', 'destino_interesse')

    # Ações rápidas (marcar como contatado)
    actions = ['marcar_como_contatado']

    def marcar_como_contatado(self, request, queryset):
        """Ação para marcar os leads selecionados como 'contatados'."""
        updated = queryset.update(foi_contatado=True)
        self.message_user(request, f'{updated} leads foram marcados como contatados.')
    marcar_como_contatado.short_description = "Marcar Leads Selecionados como Contatados"

# ==============================================================================
# Customização para o Conteúdo da Landing Page
# ==============================================================================
@admin.register(ConteudoLandingPage)
class ConteudoLandingPageAdmin(admin.ModelAdmin):
    # Garante que só haja um único registro para gerenciar
    def has_add_permission(self, request):
        return not ConteudoLandingPage.objects.exists()

    # Define a ordem dos campos no formulário de edição
    fieldsets = (
        ('Textos Principais', {
            'fields': ('titulo_principal', 'subtitulo_oferta', 'descricao_oferta')
        }),
        ('Detalhes da Oferta', {
            'fields': ('valor_oferta', 'parcelamento_max')
        }),
        ('Branding e Imagem', {
            'fields': ('nome_agencia', 'imagem_url')
        }),
    )
    list_display = ('nome_agencia', 'titulo_principal') # Exibe na lista

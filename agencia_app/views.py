# agencia_app/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings # IMPORTANTE: Importar settings para ler variáveis
from .models import Lead, ConfiguracaoLandingPage 
from urllib.parse import quote 


# O número de telefone agora é lido de settings, garantindo que seja uma variável de ambiente
try:
    # Tenta ler a variável configurada no settings.py
    NUMERO_WHATSAPP_AGENCIA = settings.NUMERO_WHATSAPP_AGENCIA
except AttributeError:
    # Fallback de segurança caso a variável não exista no settings
    NUMERO_WHATSAPP_AGENCIA = "5561983163710"


# Sua view principal para a Landing Page
def landing_page(request):
    """
    Exibe a Landing Page, carregando o conteúdo dinâmico do CMS.
    Garante que o site não quebre se o registro CMS ainda não existir.
    """
    try:
        # Tenta buscar a ÚNICA instância de configuração (CMS)
        conteudo = ConfiguracaoLandingPage.objects.get()
    except ObjectDoesNotExist:
        # Se o registro ainda não existir (primeiro acesso ao CMS), 
        # cria um objeto vazio ou com defaults para não quebrar o site
        conteudo = ConfiguracaoLandingPage() 
        
    context = {
        'conteudo': conteudo, # Variável usada no index.html ({{ conteudo.titulo_principal }})
    }
    
    # Esta view renderiza o template 'index.html' com o contexto (conteúdo do CMS)
    return render(request, 'index.html', context)


@require_POST
def capturar_lead(request):
    """
    Processa o formulário de captação de Leads, salva no banco de dados
    e redireciona o usuário para o WhatsApp.
    """
    # 1. Receber os dados do formulário (incluindo os novos campos)
    nome = request.POST.get('nome')
    email = request.POST.get('email')
    telefone = request.POST.get('telefone')
    destino_interesse = request.POST.get('destino_interesse')
    
    # NOVOS CAMPOS: Ler do formulário
    budget_disponivel = request.POST.get('budget_disponivel')
    previsao_data = request.POST.get('previsao_data')
    
    # Opcional: Adicionar validação de dados (pelo menos os obrigatórios)
    # Você deve forçar budget e previsao no frontend se for crucial
    if not all([nome, email, telefone]):
         # Redireciona de volta em caso de campos obrigatórios vazios
         return redirect(reverse('landing_page'))
    
    try:
        # 2. Salvar ou Atualizar o Lead no banco de dados
        lead, created = Lead.objects.update_or_create(
            email=email, # Campo para buscar a existência
            defaults={
                'nome': nome,
                'telefone': telefone,
                'destino_interesse': destino_interesse,
                'budget_disponivel': budget_disponivel, # <-- SALVANDO NOVO CAMPO
                'previsao_data': previsao_data,       # <-- SALVANDO NOVO CAMPO
                'origem': "Landing Page - Formulario"
            }
        )
        
        # --- 3. Preparar a URL do WhatsApp ---
        
        # Mensagem pré-preenchida para o atendente
        mensagem_base = (
            f"Olá! Sou o(a) {nome} e acabei de me cadastrar na Landing Page da FSR Viagens. "
            f"Meu destino de interesse principal é: {destino_interesse}. "
            f"Meu orçamento é de: {budget_disponivel} e pretendo viajar em: {previsao_data}. " # <-- Detalhes importantes
            f"Meu contato para retorno é: {telefone}. Por favor, me ajudem com o planejamento!"
        )
        
        # Usamos quote para garantir que a mensagem se encaixe na URL
        mensagem_formatada = quote(mensagem_base)
        
        # URL de redirecionamento final
        url_whatsapp = (
            f"https://api.whatsapp.com/send?"
            f"phone={NUMERO_WHATSAPP_AGENCIA}&"
            f"text={mensagem_formatada}"
        )
        
        # 4. Redirecionar o usuário
        return redirect(url_whatsapp)
        
    except Exception as e:
        # Em caso de qualquer erro de banco de dados ou lógica
        print(f"Erro ao salvar o lead: {e}")
        # Retorna para a página principal (Em produção, usaria-se uma mensagem de erro temporária)
        return redirect(reverse('landing_page'))

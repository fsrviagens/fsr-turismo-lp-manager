# agencia_app/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings 
from .models import Lead, ConfiguracaoLandingPage # Certifique-se de que ConfiguracaoLandingPage está importado
from urllib.parse import quote 
from django.db.models import Count # Adicionado para o Dashboard (Passo 7)

# ... (Seu código de NUMERO_WHATSAPP_AGENCIA está OK) ...
try:
    NUMERO_WHATSAPP_AGENCIA = settings.NUMERO_WHATSAPP_AGENCIA
except AttributeError:
    NUMERO_WHATSAPP_AGENCIA = "5561983163710"


def landing_page(request):
    """ Exibe a Landing Page, carregando o conteúdo dinâmico do CMS. """
    
    # CORREÇÃO/AJUSTE: Usar o método .load() do Model para garantir o objeto CMS
    conteudo = ConfiguracaoLandingPage.load()
    
    # NOTA: O tratamento de erros (form.errors) será feito diretamente no template
    context = {
        'conteudo': conteudo, 
    }
    
    return render(request, 'index.html', context)


@require_POST
def capturar_lead(request):
    """
    Processa a submissão do formulário, salva o lead e redireciona para o WhatsApp.
    """
    try:
        # 1. Recuperar dados do formulário
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        destino_interesse = request.POST.get('destino_interesse', '').strip()
        
        # Recuperar os campos com CHOICES. O HTML deve enviar os valores válidos
        budget_disponivel = request.POST.get('budget_disponivel', 'Nao_Informado')
        previsao_data = request.POST.get('previsao_data', 'Flexivel')
        
        # 2. Validação Básica (Verifica se campos obrigatórios estão preenchidos)
        if not all([nome, email, telefone, destino_interesse]):
            # Redireciona de volta para a LP se faltar campos CRÍTICOS
            # Uma mensagem de erro seria ideal aqui, mas por simplicidade, apenas redirecionamos.
            return redirect(reverse('landing_page'))

        # 3. Salvar o Lead
        Lead.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            destino_interesse=destino_interesse,
            budget_disponivel=budget_disponivel,
            previsao_data=previsao_data, 
            origem="Landing Page - Formulario"
        )
        
        # ... (O resto do seu código de preparo de URL do WhatsApp está OK) ...
        # Mensagem pré-preenchida para o atendente
        mensagem_base = (
            f"Olá! Sou o(a) {nome} e acabei de me cadastrar na Landing Page da FSR Viagens. "
            f"Meu destino de interesse principal é: {destino_interesse}. "
            f"Meu orçamento é de: {budget_disponivel} e pretendo viajar em: {previsao_data}. "
            f"Meu contato para retorno é: {telefone}. Por favor, me ajudem com o planejamento!"
        )
        
        mensagem_formatada = quote(mensagem_base)
        
        url_whatsapp = (
            f"https://api.whatsapp.com/send?"
            f"phone={NUMERO_WHATSAPP_AGENCIA}&"
            f"text={mensagem_formatada}"
        )
        
        # 4. Redirecionar o usuário
        return redirect(url_whatsapp)
        
    except Exception as e:
        print(f"Erro ao salvar o lead: {e}")
        # Em produção, deve-se logar este erro. Redireciona para evitar quebra.
        return redirect(reverse('landing_page'))


# NOVO: Implementação do Dashboard de Leads (Passo 7)
def dashboard_leads(request):
    """
    Exibe um mini-dashboard com as principais estatísticas de qualificação de leads.
    """
    
    if not request.user.is_authenticated:
        return redirect(reverse('admin:login')) 

    total_leads = Lead.objects.count()

    # Usando os nomes dos campos no banco de dados (que correspondem aos Choices)
    leads_por_budget = Lead.objects.values('budget_disponivel').annotate(
        count=Count('budget_disponivel')
    ).order_by('-count')
    
    leads_por_previsao = Lead.objects.values('previsao_data').annotate(
        count=Count('previsao_data')
    ).order_by('-count')

    leads_por_destino = Lead.objects.values('destino_interesse').annotate(
        count=Count('destino_interesse')
    ).exclude(
        destino_interesse__in=['Não Informado', '']
    ).order_by('-count')[:5] 
    
    # Altos Valores: Exemplo (o valor deve ser o valor chave do Choice, não a descrição)
    altos_valores = Lead.objects.filter(budget_disponivel='20K+').count()

    context = {
        'total_leads': total_leads,
        'leads_por_budget': leads_por_budget,
        'leads_por_previsao': leads_por_previsao,
        'leads_por_destino': leads_por_destino,
        'altos_valores': altos_valores,
    }
    
    # NOTA: Você precisará criar o template 'dashboard.html'
    return render(request, 'dashboard.html', context)


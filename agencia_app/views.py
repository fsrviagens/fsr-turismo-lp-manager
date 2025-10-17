# agencia_app/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Lead, ConfiguracaoLandingPage # Importar o modelo CMS
from urllib.parse import quote 
from django.core.exceptions import ObjectDoesNotExist # Útil para o CMS

# Número de telefone fixo da agência para o WhatsApp (com código do país e área)
NUMERO_WHATSAPP_AGENCIA = "5561983163710" 

# Sua view principal para a Landing Page
def landing_page(request):
    """
    Exibe a Landing Page, carregando o conteúdo dinâmico do CMS.
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
    # 1. Receber os dados do formulário (incluindo o novo campo)
    nome = request.POST.get('nome')
    email = request.POST.get('email')
    telefone = request.POST.get('telefone')
    destino_interesse = request.POST.get('destino_interesse') # <-- NOVO CAMPO
    
    # Opcional: Adicionar validação de dados
    if not all([nome, email, telefone, destino_interesse]):
         # Redireciona de volta em caso de campos obrigatórios vazios
         # Em um ambiente de produção, adicionaríamos mensagens de erro (Django Messages)
         return redirect(reverse('landing_page'))
    
    try:
        # 2. Salvar o Lead no banco de dados
        # Usamos update_or_create para evitar erro se o email já existir (unique=True)
        lead, created = Lead.objects.update_or_create(
            email=email, # Campo para buscar a existência
            defaults={
                'nome': nome,
                'telefone': telefone,
                'destino_interesse': destino_interesse,
                'origem': "Landing Page - Formulario"
            }
        )
        
        # --- 3. Preparar a URL do WhatsApp ---
        
        # Mensagem pré-preenchida para o atendente
        mensagem_base = (
            f"Olá! Sou o(a) {nome} e acabei de me cadastrar na Landing Page da FSR Viagens. "
            f"Meu destino de interesse principal é: {destino_interesse}. " # <-- Detalhe importante
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
        # Retorna para a página principal (podemos usar uma mensagem de erro temporária aqui)
        return redirect(reverse('landing_page'))

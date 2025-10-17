from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from urllib.parse import quote
from .models import Lead, ConteudoLandingPage
import os

# Número de telefone da agência (ajustado para o formato WhatsApp)
WHATSAPP_NUMBER = "5561983163710"

# ==============================================================================
# VIEW 1: RENDERIZAÇÃO DA LANDING PAGE
# ==============================================================================
def landing_page(request):
    """
    Carrega o conteúdo mais recente do ConteudoLandingPage e 
    renderiza o rascunho HTML com os dados dinâmicos.
    """
    try:
        # Pega o primeiro (e único) registro de conteúdo. 
        conteudo = ConteudoLandingPage.objects.first()
        if not conteudo:
             # Cria um objeto com valores padrão caso o banco esteja vazio
             conteudo = ConteudoLandingPage() 
             
    except Exception as e:
        # Se houver erro de banco de dados, usa um objeto vazio para não quebrar.
        print(f"Erro ao carregar Conteúdo da Landing Page: {e}")
        conteudo = ConteudoLandingPage()

    context = {
        'conteudo': conteudo,
        'form_submitted': request.session.pop('form_submitted', False), # Para mostrar mensagem de sucesso
    }
    # Aqui, a view vai carregar o HTML que definiremos a seguir (templates/index.html)
    return render(request, 'index.html', context)

# ==============================================================================
# VIEW 2: PROCESSAMENTO DO FORMULÁRIO DE LEAD
# ==============================================================================
@require_POST # Garante que esta view só responda a requisições POST (envio de formulário)
def capturar_lead(request):
    """
    Valida os dados do formulário, salva o Lead no banco de dados 
    e redireciona para o WhatsApp com a mensagem pré-preenchida.
    """
    
    # 1. Coleta e sanitiza os dados do formulário
    nome = request.POST.get('nome', '').strip()
    email = request.POST.get('email', '').strip()
    telefone = request.POST.get('telefone', '').strip()
    destino_interesse = request.POST.get('destino_interesse', '').strip()
    
    # 2. Validação Mínima (todos os campos são obrigatórios pelo modelo)
    if not all([nome, email, telefone, destino_interesse]):
        print("Erro: Todos os campos são obrigatórios.")
        return redirect('agencia_app:landing_page')

    try:
        # 3. Salva o Lead no banco de dados (Supabase/PostgreSQL)
        lead = Lead.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            destino_interesse=destino_interesse
        )
        
        # Define uma flag para exibir a mensagem de sucesso após o redirect
        # Note que precisamos da chave 'session' para isso funcionar.
        request.session['form_submitted'] = True 
        
        # 4. Constrói a Mensagem Pré-preenchida para o WhatsApp
        conteudo = ConteudoLandingPage.objects.first()
        valor = f"R${conteudo.valor_oferta:.2f} ({conteudo.parcelamento_max}x)" if conteudo else "a oferta principal"

        message_template = (
            f"Olá, FSR Turismo! Meu nome é {nome} e sou um novo lead interessado em viagens."
            f"\n\nDetalhes do meu interesse:"
            f"\n- Destino Desejado: {destino_interesse}"
            f"\n- Oferta Vista: {valor}"
            f"\n- Meu Telefone: {telefone}"
            f"\n\nAguardo o contato para planejarmos juntos!"
        )
        
        # Codifica a URL para o WhatsApp
        whatsapp_url = (
            f"https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}"
            f"&text={quote(message_template)}"
        )
        
        # 5. Redireciona o usuário para o link do WhatsApp
        return redirect(whatsapp_url)

    except Exception as e:
        print(f"Erro ao salvar o Lead ou processar: {e}")
        # Em caso de erro (ex: e-mail duplicado), redireciona de volta
        return redirect('agencia_app:landing_page')

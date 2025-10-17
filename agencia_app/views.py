# agencia_app/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods
from .models import Lead
from urllib.parse import quote # Ajuda a formatar mensagens de URL

# Sua view principal para a Landing Page
def landing_page(request):
    """
    Exibe a Landing Page. Se houver métodos POST, o processamento será feito
    por uma view separada (melhor prática).
    """
    # Esta view simplesmente renderiza o template 'index.html'
    return render(request, 'index.html')


@require_POST
def capturar_lead(request):
    """
    Processa o formulário de captação de Leads, salva no banco de dados
    e redireciona o usuário para o WhatsApp.
    """
    if request.method == 'POST':
        # 1. Receber os dados do formulário
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        
        # Opcional: Adicionar validação de dados (por exemplo, se campos são vazios)
        if not all([nome, email, telefone]):
             # Caso falte algum dado, podemos redirecionar de volta com uma mensagem de erro
             # (Em uma solução completa, usaríamos Django Forms para melhor validação)
             return redirect(reverse('landing_page'))
        
        try:
            # 2. Salvar o Lead no banco de dados
            lead = Lead.objects.create(
                nome=nome,
                email=email,
                telefone=telefone,
                origem="Landing Page" # Opcional: Garante a origem
            )
            # O objeto lead agora tem um ID
            
            # --- 3. Preparar a URL do WhatsApp ---
            
            # O número de telefone da sua agência (com código do país e área, sem caracteres especiais)
            # Exemplo: 5521988887777 (55 = Brasil, 21 = DDD)
            NUMERO_WHATSAPP_AGENCIA = "5561983163710" # <--- **AJUSTE AQUI**
            
            # Mensagem pré-preenchida para o atendente
            mensagem_base = (
                f"Olá! Sou o(a) {nome} e acabei de me cadastrar na landing page. "
                f"Meu email é {email}. Tenho interesse em uma viagem!"
            )
            
            # Usamos quote para garantir que a mensagem se encaixe na URL sem problemas
            mensagem_formatada = quote(mensagem_base)
            
            # URL de redirecionamento final para o WhatsApp
            url_whatsapp = (
                f"https://api.whatsapp.com/send?"
                f"phone={NUMERO_WHATSAPP_AGENCIA}&"
                f"text={mensagem_formatada}"
            )
            
            # 4. Redirecionar o usuário
            return redirect(url_whatsapp)
            
        except Exception as e:
            # Captura erros, como email duplicado (unique=True em models.py)
            print(f"Erro ao salvar o lead: {e}")
            # Em caso de erro, redireciona de volta para a landing page.
            return redirect(reverse('landing_page'))
            
    # Se a requisição não for POST (o que não deve acontecer por causa do @require_POST), apenas redireciona.
    return redirect(reverse('landing_page')) 

# Documentação:
# - @require_POST: Decorador que garante que esta função só aceita requisições POST (submissão de formulário).
# - request.POST.get(): Método para extrair dados do formulário enviado.
# - Lead.objects.create(): Método do Django ORM para criar e salvar um novo objeto (linha) no banco de dados.
# - urllib.parse.quote(): Essencial para codificar a mensagem do WhatsApp para que funcione em um URL.
# - reverse('landing_page'): Usado para obter a URL da 'landing_page' (definida em urls.py) pelo nome.

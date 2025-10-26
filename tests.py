# agencia_app/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch
from .models import Lead, ConfiguracaoLandingPage, BUDGET_CHOICES, PREVISAO_CHOICES
import urllib.parse
from django.core.exceptions import ValidationError

# ====================================================================
# 1. TESTES DE MODELOS (Models)
# ====================================================================

class ModelTests(TestCase):
    """
    Testes unitários para garantir o correto funcionamento dos modelos.
    """
    
    def test_create_lead(self):
        """Testa a criação básica de um Lead."""
        lead = Lead.objects.create(
            nome="Tester Lead",
            email="tester@fsr.com",
            telefone="5561988887777",
            destino_interesse="Ilhas Gregas",
            # Testa o uso dos CHOICES
            budget_disponivel='10K_20K',
            previsao_data='6M'
        )
        self.assertEqual(lead.nome, "Tester Lead")
        self.assertTrue(Lead.objects.exists())
        self.assertEqual(lead.budget_disponivel, '10K_20K')
        self.assertEqual(lead.origem, 'Landing Page') # Testando o default
        
    def test_lead_email_unique(self):
        """Testa se o email é único (unique=True)."""
        Lead.objects.create(
            nome="Lead Um", 
            email="unico@fsr.com", 
            telefone="5511911110000"
        )
        # Tentar criar um segundo Lead com o mesmo email deve falhar
        with self.assertRaises(Exception):
            Lead.objects.create(
                nome="Lead Dois", 
                email="unico@fsr.com", 
                telefone="5511922220000"
            )

    def test_singleton_configuracao_creation(self):
        """Testa se apenas uma Configuração pode ser criada."""
        # Cria a primeira instância (deve ser sucesso)
        ConfiguracaoLandingPage.objects.create(
            titulo_principal="Configuração Teste 1"
        )
        self.assertEqual(ConfiguracaoLandingPage.objects.count(), 1)

        # Tenta criar a segunda instância (deve gerar ValidationError)
        with self.assertRaises(ValidationError):
            ConfiguracaoLandingPage.objects.create(
                titulo_principal="Configuração Teste 2"
            )

# ====================================================================
# 2. TESTES DE VIEWS (Funcionalidade HTTP)
# ====================================================================

class ViewTests(TestCase):
    """
    Testes funcionais para as views 'landing_page' e 'capturar_lead'.
    """
    
    def setUp(self):
        # Configurações iniciais para cada teste
        self.client = Client()
        self.landing_page_url = reverse('landing_page')
        self.capturar_lead_url = reverse('capturar_lead')
        
        # Cria um registro CMS para o teste de visualização
        ConfiguracaoLandingPage.objects.create(
            titulo_principal="Oferta de Verão",
            valor_oferta=500.00
        )

    def test_landing_page_get(self):
        """Testa se a landing page carrega o template correto e o conteúdo CMS."""
        response = self.client.get(self.landing_page_url)
        
        # 1. Deve retornar um código de status 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # 2. Deve usar o template correto
        self.assertTemplateUsed(response, 'index.html')
        
        # 3. Deve ter o conteúdo do CMS no contexto
        self.assertIn('Oferta de Verão', response.content.decode())
        
    def test_capturar_lead_post_success_and_whatsapp_redirect(self):
        """Testa o envio do formulário e o redirecionamento para o WhatsApp."""
        
        # Simula os dados do formulário (que correspondem aos campos do models.py)
        data = {
            'nome': 'Testador Completo',
            'email': 'form_test@fsr.com',
            'telefone': '5561999990000',
            'destino_interesse': 'Cancun',
            'budget_disponivel': '20K+',
            'previsao_data': '3M',
        }

        # Simula a requisição POST
        response = self.client.post(self.capturar_lead_url, data)

        # 1. Verifica se o Lead foi salvo no banco de dados
        self.assertTrue(Lead.objects.filter(email='form_test@fsr.com').exists())
        
        # 2. Verifica se houve um redirecionamento (código 302)
        self.assertEqual(response.status_code, 302)
        
        # 3. Verifica o URL de redirecionamento para o WhatsApp
        redirect_url = response.url
        self.assertIn("https://api.whatsapp.com/send?", redirect_url)
        self.assertIn(settings.NUMERO_WHATSAPP_AGENCIA, redirect_url) # Testa a variável de ambiente
        
        # 4. Verifica se a mensagem pré-preenchida está na URL
        parsed_url = urllib.parse.urlparse(redirect_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Verifica a mensagem (deve conter o nome e destino)
        mensagem = query_params.get('text', [''])[0]
        self.assertIn("Testador Completo", mensagem)
        self.assertIn("Cancun", mensagem)
        self.assertIn("20K+", mensagem) # Verifica se os dados dos CHOICES foram para a mensagem
        self.assertIn("3M", mensagem) # Verifica se os dados dos CHOICES foram para a mensagem
        
    def test_capturar_lead_get_denied(self):
        """Testa se o acesso via GET é rejeitado pelo decorator @require_POST."""
        response = self.client.get(self.capturar_lead_url)
        # O @require_POST deve retornar 405 (Method Not Allowed) ou redirecionar
        self.assertEqual(response.status_code, 405)


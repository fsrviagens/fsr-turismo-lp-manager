# agencia_app/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Count # Adicionado para uso na Regra Singleton

# ===================================================================
# CHOICES (Boas Práticas: Usar para dados categóricos)
# ===================================================================

BUDGET_CHOICES = [
    ('5K_10K', 'R$5.000 - R$10.000'),
    ('10K_20K', 'R$10.000 - R$20.000'),
    ('20K+', 'Acima de R$20.000'),
    ('Nao_Informado', 'Não Informado'),
]

PREVISAO_CHOICES = [
    ('3M', 'Próximos 3 meses'),
    ('6M', 'Próximos 6 meses'),
    ('1A', 'Próximo Ano'),
    ('Flexivel', 'Flexível/Indefinido'),
]


# ===================================================================
# 1. MODELO PARA CAPTURA DE LEADS
# ===================================================================

class Lead(models.Model):
    # ... (Seus campos nome, email, telefone, data_cadastro, origem estão OK) ...
    nome = models.CharField(max_length=100, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, verbose_name="Email de Contato")
    telefone = models.CharField(max_length=20, verbose_name="Telefone (WhatsApp)")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    origem = models.CharField(max_length=100, default='Landing Page')

    # CORREÇÃO/AJUSTE: Implementar os Choices nos campos de qualificação
    destino_interesse = models.CharField(
        max_length=150, 
        verbose_name="Destino de Interesse",
        default="Não Informado" # Adicionado Default
    )
    budget_disponivel = models.CharField(
        max_length=20,
        choices=BUDGET_CHOICES, # Usa a lista de Choices
        default='Nao_Informado',
        verbose_name="Orçamento Estimado"
    )
    previsao_data = models.CharField(
        max_length=20,
        choices=PREVISAO_CHOICES, # Usa a lista de Choices
        default='Flexivel',
        verbose_name="Previsão de Viagem"
    )
    
    class Meta:
        verbose_name = "Lead de Vendas"
        verbose_name_plural = "Leads de Vendas"
        ordering = ['-data_cadastro']
        
    def __str__(self):
        return f"Lead: {self.nome} - Destino: {self.destino_interesse}"


# ===================================================================
# 2. MODELO PARA CMS (Configuração da Landing Page)
# ===================================================================

class ConfiguracaoLandingPage(models.Model):
    # ... (Seus campos de título, logo, imagem, etc. estão OK) ...
    nome_agencia = models.CharField(max_length=100, default="FSR Viagens")
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    titulo_principal = models.CharField(max_length=255, default="Sua próxima viagem começa aqui!")
    subtitulo_oferta = models.TextField(max_length=500, default="Descubra pacotes exclusivos nas melhores operadoras.")
    imagem_url = models.URLField(max_length=500, verbose_name="URL da Imagem de Destaque")
    valor_oferta = models.DecimalField(max_digits=10, decimal_places=2, default=999.00, verbose_name="Valor 'A partir de' (R$)")
    parcelamento_max = models.PositiveSmallIntegerField(default=12, verbose_name="Máximo de Parcelas")
    descricao_oferta = models.TextField(verbose_name="Descrição Detalhada da Oferta")
    parcelamento_detalhe = models.CharField(max_length=255, default="Em até 12x sem juros de R$83,25")
    
    class Meta:
        verbose_name = "Configuração da Landing Page (CMS)"
        verbose_name_plural = "Configuração da Landing Page (CMS)"

    def __str__(self):
        return f"Configurações Atuais da Landing Page"
    
    # CORREÇÃO CRÍTICA: Implementar a Regra Singleton para garantir apenas 1 registro no CMS
    def save(self, *args, **kwargs):
        if self.__class__.objects.count() >= 1 and not self.pk:
            # Se tentar criar um segundo registro, dispara um erro de validação.
            raise ValidationError("Só pode haver UMA Configuração de Landing Page. Por favor, edite a existente.")
        super().save(*args, **kwargs)

    # CORREÇÃO: Método para garantir que o objeto Singleton seja sempre retornado
    @classmethod
    def load(cls):
        if cls.objects.count() == 0:
            return cls.objects.create() # Cria uma instância com defaults se não existir
        return cls.objects.get() # Retorna o único objeto existente

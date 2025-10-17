# agencia_app/models.py

from django.db import models

# ====================================================================
# 1. MODELO PARA CAPTURA DE LEADS
# ====================================================================

class Lead(models.Model):
    """
    Modelo para armazenar informações de um Lead (potencial cliente) capturado
    pelo formulário da Landing Page.
    """
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome Completo"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email de Contato"
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name="Telefone (WhatsApp)"
    )
    destino_interesse = models.CharField(
        max_length=150,
        blank=True,
        null=True, 
        verbose_name="Destino de Interesse Principal"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    origem = models.CharField(
        max_length=50,
        default='Landing Page',
        verbose_name="Origem do Lead"
    )

    class Meta:
        ordering = ['-data_cadastro']
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self):
        return f"{self.nome} ({self.destino_interesse or 'Sem Destino'})"


# ====================================================================
# 2. MODELO PARA O CMS SIMPLES (Configuração da Landing Page)
# ====================================================================

class ConfiguracaoLandingPage(models.Model):
    """
    Modelo para armazenar as configurações de conteúdo da Landing Page.
    Ele é projetado para ter APENAS UM REGISTRO no banco de dados.
    """
    
    # Informações Básicas
    nome_agencia = models.CharField(
        max_length=100,
        default="FSR Viagens & Turismo",
        verbose_name="Nome da Agência"
    )
    logo_url = models.URLField(
        verbose_name="URL do Logo",
        blank=True,
        null=True,
        help_text="URL pública do logo da agência (opcional)."
    )
    
    # Campos da Seção HERO (Destaque Principal)
    titulo_principal = models.CharField(
        max_length=200,
        default="OFERTA EXCLUSIVA DE VIAGENS INTERNACIONAIS!",
        verbose_name="Título Principal (Hero)"
    )
    subtitulo_oferta = models.CharField(
        max_length=300,
        default="Planeje sua viagem dos sonhos com segurança e flexibilidade.",
        verbose_name="Subtítulo da Oferta"
    )
    imagem_url = models.URLField(
        verbose_name="URL da Imagem de Fundo (Hero)",
        help_text="Link para a imagem de alta qualidade que aparece no topo da página.",
        default="https://images.unsplash.com/photo-1542010589005-d1eacc394a2a?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    )
    
    # Campos Financeiros
    valor_oferta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=999.00,
        verbose_name="Valor 'A partir de' (R$)"
    )
    parcelamento_max = models.PositiveSmallIntegerField(
        default=12,
        verbose_name="Máximo de Parcelas"
    )
    
    # Campos de Descrição
    descricao_oferta = models.TextField(
        verbose_name="Descrição Detalhada da Oferta",
        help_text="Use parágrafos ou quebras de linha para melhor visualização.",
        default="A FSR Viagens está pronta para transformar seu sonho em realidade. Nossos pacotes exclusivos incluem seguro viagem, passagens e hospedagem nos melhores destinos. Clique e saiba mais!"
    )
    
    class Meta:
        verbose_name = "Configuração da Landing Page (CMS)"
        verbose_name_plural = "Configuração da Landing Page (CMS)"

    def __str__(self):
        return f"Configurações Atuais da Landing Page"
    
    # Regra: Limita a APENAS um registro no banco de dados.
    def save(self, *args, **kwargs):
        if self.__class__.objects.count() >= 1 and not self.id:
            from django.core.exceptions import ValidationError
            raise ValidationError("Você só pode ter uma configuração de Landing Page. Edite a existente.")
        super(ConfiguracaoLandingPage, self).save(*args, **kwargs)

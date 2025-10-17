from django.db import models

# ==============================================================================
# 1. MODELO DE CONTEÚDO DA LANDING PAGE
# ==============================================================================
class ConteudoLandingPage(models.Model):
    """Modelo que define o conteúdo dinâmico da Landing Page."""

    # Textos da Landing Page
    titulo_principal = models.CharField(max_length=200, default="Sua próxima grande viagem começa aqui.")
    subtitulo_oferta = models.CharField(max_length=400, default="O destino dos seus sonhos, com as melhores condições do mercado.")
    descricao_oferta = models.TextField(default="Descubra ofertas exclusivas para destinos selecionados. Planejamento personalizado, flexibilidade e segurança total.")

    # Informações da Oferta (Valor e Parcelamento)
    valor_oferta = models.DecimalField(max_digits=10, decimal_places=2, default=999.99, verbose_name="Valor Promocional (R$)")
    parcelamento_max = models.IntegerField(default=12, verbose_name="Parcelamento Máximo (x)")

    # Elementos de Contato/Branding
    nome_agencia = models.CharField(max_length=100, default="FSR Turismo")

    # Imagem Principal (Guarda apenas o caminho ou URL)
    imagem_url = models.URLField(
        default="https://placehold.co/1200x600/293241/ffffff?text=Imagem+Gerenciável+da+Oferta",
        verbose_name="URL da Imagem Principal"
    )

    class Meta:
        verbose_name = "Conteúdo da Landing Page"
        verbose_name_plural = "Conteúdos da Landing Page"

    def __str__(self):
        return f"Configuração do Conteúdo - ID: {self.id}"

# ==============================================================================
# 2. MODELO DE LEAD (Cliente Potencial)
# ==============================================================================
class Lead(models.Model):
    """Modelo que armazena os dados dos leads capturados."""

    # Dados Obrigatórios
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True) # E-mail único para evitar duplicidade de leads
    telefone = models.CharField(max_length=20, verbose_name="Telefone com DDD")

    # Dado Adicional Solicitado
    destino_interesse = models.CharField(max_length=255, verbose_name="Destino de Interesse")

    # Metadata
    data_captura = models.DateTimeField(auto_now_add=True, verbose_name="Data de Captura")
    foi_contatado = models.BooleanField(default=False, verbose_name="Lead Contatado")

    class Meta:
        verbose_name = "Lead Capturado"
        verbose_name_plural = "Leads Capturados"
        # Ordena os leads por data de captura, do mais novo para o mais antigo
        ordering = ['-data_captura']

    def __str__(self):
        return self.nome

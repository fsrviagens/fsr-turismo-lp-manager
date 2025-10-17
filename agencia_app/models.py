# agencia_app/models.py

from django.db import models

class Lead(models.Model):
    """
    Modelo para armazenar informações de um Lead (potencial cliente).
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
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    
    # Campo opcional para rastrear de onde o lead veio (ex: 'form_landing_page')
    origem = models.CharField(
        max_length=50,
        default='Landing Page',
        verbose_name="Origem do Lead"
    )

    class Meta:
        # Define a ordem padrão dos Leads (os mais recentes primeiro)
        ordering = ['-data_cadastro']
        # Nome amigável no singular
        verbose_name = "Lead"
        # Nome amigável no plural (aparecerá na área admin)
        verbose_name_plural = "Leads"

    def __str__(self):
        """
        Representação em string do objeto, útil para o Admin.
        """
        return f"{self.nome} - {self.email}"

# Documentação:
# - models.Model: É a base para todos os modelos no Django, mapeando para uma tabela.
# - CharField: Campo de texto curto (máx. 100 caracteres para nome).
# - EmailField: Campo que garante o formato de email e 'unique=True' impede emails duplicados.
# - DateTimeField: Armazena data e hora. 'auto_now_add=True' preenche automaticamente na criação.
# - Meta: Classe interna para metadados do modelo (como ordem, nomes amigáveis).
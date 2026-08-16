from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Usuário customizado do FinAtlas.

    Substitui o `User` padrão do Django desde o início do projeto para
    permitir múltiplos papéis (`role`) e vínculo com uma organização
    (`organization`), sem exigir uma migração destrutiva no futuro.
    """

    class Role(models.TextChoices):
        SAAS_ADMIN = "SAAS_ADMIN", "SaaS Admin"
        FINANCEIRO = "FINANCEIRO", "Financeiro"
        ASSESSOR = "ASSESSOR", "Assessor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        help_text="Papel do usuário no sistema. Define quais telas e dados ele pode acessar.",
    )

    # Nula para o SaaS Admin, que não pertence a nenhuma organização.
    # Obrigatória (validada na camada de aplicação) para Financeiro e Assessor.
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
        help_text="Organização (tenant) à qual este usuário pertence. Vazio apenas para SaaS Admin.",
    )

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_saas_admin(self):
        return self.role == self.Role.SAAS_ADMIN

    @property
    def is_financeiro(self):
        return self.role == self.Role.FINANCEIRO

    @property
    def is_assessor(self):
        return self.role == self.Role.ASSESSOR


class AdvisorProfile(models.Model):
    """
    Dados específicos do papel Assessor.

    Mantido fora do `User` para não misturar dados de domínio financeiro
    com o modelo de autenticação (regra da seção 11 do Prompt Master 2.0).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="advisor_profile",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="advisor_profiles",
        help_text="Redundante em relação a user.organization; mantido para simplificar queries e filtros.",
    )
    codigo_assessor = models.CharField(
        max_length=50,
        help_text="Código usado nos arquivos importados (PJ1, PJ2 Previdência) para identificar este assessor.",
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "codigo_assessor"],
                name="codigo_assessor_unico_por_organizacao",
            )
        ]

    def __str__(self):
        return f"{self.user} ({self.codigo_assessor})"

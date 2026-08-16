from django.db import models


class Company(models.Model):
    """
    Representa uma das empresas internas de uma organização (ex.: PJ1,
    PJ2, Plus, dentro da Accanto).

    Sempre vinculada a uma Organization — é o segundo nível de
    isolamento multi-tenant (organização -> empresa -> produto/lançamento).
    """

    class Tipo(models.TextChoices):
        PJ1 = "PJ1", "PJ1"
        PJ2 = "PJ2", "PJ2"
        PLUS = "PLUS", "Plus"

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="companies",
    )
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "nome"],
                name="nome_empresa_unico_por_organizacao",
            )
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Product(models.Model):
    """
    Produto oferecido por uma Company. O isolamento por organização é
    indireto, via `company.organization` — por isso toda query de
    Product feita em uma view deve filtrar por
    `company__organization=request.user.organization`.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="products",
    )
    nome = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "nome"],
                name="nome_produto_unico_por_empresa",
            )
        ]

    def __str__(self):
        return f"{self.nome} — {self.company.nome}"


class Commission(models.Model):
    """
    Percentual de comissão de um assessor, versionado por mês/ano de
    vigência (ex.: Assessor A, 01/2026 -> 60%, 02/2026 -> 65%).

    O valor aplicado a cada lançamento (Entry) é copiado — snapshot —
    no momento do processamento (Etapas 5-7). Por isso, alterar uma
    Commission aqui NUNCA modifica lançamentos já processados.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="commissions",
    )
    advisor = models.ForeignKey(
        "accounts.AdvisorProfile",
        on_delete=models.PROTECT,
        related_name="commissions",
    )
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    mes_referencia = models.PositiveSmallIntegerField()
    ano_referencia = models.PositiveSmallIntegerField()
    criado_por = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="commissions_criadas",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ano_referencia", "-mes_referencia"]
        constraints = [
            models.UniqueConstraint(
                fields=["advisor", "mes_referencia", "ano_referencia"],
                name="uma_comissao_por_assessor_por_mes",
            ),
            models.CheckConstraint(
                condition=models.Q(mes_referencia__gte=1)
                & models.Q(mes_referencia__lte=12),
                name="mes_referencia_valido",
            ),
        ]

    def __str__(self):
        return f"{self.advisor} — {self.mes_referencia:02d}/{self.ano_referencia}: {self.percentual}%"

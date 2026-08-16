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

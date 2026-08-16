from django.db import models


class Organization(models.Model):
    """
    Representa um tenant do FinAtlas (ex.: Accanto).

    Todo dado sensível do sistema (usuários, empresas, produtos,
    comissões, lançamentos) deve possuir uma relação direta ou indireta
    com uma Organization. É a base do isolamento multi-tenant.
    """

    nome = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

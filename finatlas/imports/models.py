from django.db import models


class ImportBatch(models.Model):
    """
    Registro de uma importação de arquivo (PJ1 ou PJ2 Previdência).

    Campos de controle de duplicidade e resumo (hash do arquivo,
    contadores) serão adicionados/utilizados na Etapa 5, quando o
    fluxo de upload for implementado. Aqui só o essencial para servir
    de FK aos modelos de Entry.
    """

    class Origem(models.TextChoices):
        PJ1 = "PJ1", "PJ1"
        PJ2_PREVIDENCIA = "PJ2_PREVIDENCIA", "PJ2 Previdência"

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="import_batches",
    )
    origem = models.CharField(max_length=20, choices=Origem.choices)
    arquivo_hash = models.CharField(max_length=64, unique=True)
    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="import_batches",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_origem_display()} — {self.criado_em:%d/%m/%Y %H:%M}"

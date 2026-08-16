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


class BaseEntry(models.Model):
    """
    Campos comuns a todo lançamento financeiro, independente da origem
    (PJ1, PJ2 Previdência, PJ2 Seguros, Plus).

    Abstrato — não vira tabela própria. Cada origem tem seu modelo
    concreto (ver abaixo) porque os campos específicos diferem entre
    elas (seção 23 do Prompt Master 2.0: "quando um campo não existir
    em uma origem, não invente o dado").
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="%(class)s_entries",
    )
    advisor = models.ForeignKey(
        "accounts.AdvisorProfile",
        on_delete=models.PROTECT,
        related_name="%(class)s_entries",
        null=True,
        blank=True,
        help_text="Nulo quando o assessor não pôde ser identificado na importação (linha fica como pendente de revisão).",
    )

    # Mês/ano ao qual o lançamento pertence para fins de histórico e
    # dashboard — não é necessariamente igual à data do lançamento
    # (ex.: um arquivo de fevereiro pode conter uma linha com data de
    # janeiro; period_referencia é o que decide em qual "mês" ele
    # aparece nos históricos).
    mes_referencia = models.PositiveSmallIntegerField()
    ano_referencia = models.PositiveSmallIntegerField()
    data_lancamento = models.DateField(
        help_text="Data original do registro na origem (planilha ou lançamento manual)."
    )

    # Nulo para lançamentos manuais (PJ2 Seguros, Plus); preenchido para
    # lançamentos vindos de importação de arquivo (PJ1, PJ2 Previdência).
    import_batch = models.ForeignKey(
        "imports.ImportBatch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_entries",
    )

    criado_por = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="%(class)s_entries_criadas",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=models.Q(mes_referencia__gte=1)
                & models.Q(mes_referencia__lte=12),
                name="%(app_label)s_%(class)s_mes_referencia_valido",
            ),
        ]


class PJ1Entry(BaseEntry):
    """Lançamento importado de arquivo PJ1 (seção 13 do Prompt Master 2.0)."""

    categoria = models.CharField(max_length=255)
    produto = models.CharField(max_length=255)
    nivel_1 = models.CharField(max_length=255, blank=True)
    nivel_2 = models.CharField(max_length=255, blank=True)
    nivel_3 = models.CharField(max_length=255, blank=True)
    codigo_cliente = models.CharField(max_length=100)

    receita = models.DecimalField(max_digits=14, decimal_places=2)
    receita_liquida = models.DecimalField(max_digits=14, decimal_places=2)

    repasse_percentual_escritorio = models.DecimalField(max_digits=5, decimal_places=2)
    comissao_bruta_escritorio = models.DecimalField(max_digits=14, decimal_places=2)

    codigo_assessor_direto = models.CharField(max_length=50)
    repasse_percentual_assessor_direto = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    comissao_assessor_direto = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Snapshot: valor já calculado no momento da importação. Não é recalculado a partir de Commission depois.",
    )

    class Meta(BaseEntry.Meta):
        constraints = BaseEntry.Meta.constraints + [
            models.UniqueConstraint(
                fields=[
                    "organization",
                    "codigo_assessor_direto",
                    "codigo_cliente",
                    "data_lancamento",
                    "comissao_bruta_escritorio",
                ],
                name="pj1entry_chave_composta_duplicidade",
            ),
        ]

    def __str__(self):
        return f"PJ1 — {self.codigo_cliente} — {self.data_lancamento}"


class PJ2PrevidenciaEntry(BaseEntry):
    """Lançamento importado de arquivo PJ2 Previdência (seção 14)."""

    classificacao = models.CharField(max_length=255)
    categoria = models.CharField(max_length=255)
    nivel_1 = models.CharField(max_length=255, blank=True)
    nivel_2 = models.CharField(max_length=255, blank=True)
    nivel_3 = models.CharField(max_length=255, blank=True)
    nivel_4 = models.CharField(max_length=255, blank=True)
    codigo_cliente = models.CharField(max_length=100)
    codigo_assessor = models.CharField(max_length=50)

    receita_bruta = models.DecimalField(max_digits=14, decimal_places=2)
    receita_liquida = models.DecimalField(max_digits=14, decimal_places=2)
    comissao_percentual_escritorio = models.DecimalField(max_digits=5, decimal_places=2)
    comissao_escritorio = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta(BaseEntry.Meta):
        constraints = BaseEntry.Meta.constraints + [
            models.UniqueConstraint(
                fields=[
                    "organization",
                    "codigo_assessor",
                    "codigo_cliente",
                    "data_lancamento",
                    "comissao_escritorio",
                ],
                name="pj2preventry_chave_composta_duplicidade",
            ),
        ]

    def __str__(self):
        return f"PJ2 Previdência — {self.codigo_cliente} — {self.data_lancamento}"


class PJ2SegurosEntry(BaseEntry):
    """
    Lançamento manual de PJ2 Seguros (seção 15). Sem import_batch (é
    sempre lançamento manual pelo Financeiro).
    """

    class Seguradora(models.TextChoices):
        PRUDENTIAL = "PRUDENTIAL", "Prudential"
        METLIFE = "METLIFE", "MetLife"
        ICATU = "ICATU", "Icatu"

    seguradora = models.CharField(max_length=20, choices=Seguradora.choices)
    produto = models.ForeignKey(
        "financial.Product", on_delete=models.PROTECT, related_name="pj2seguros_entries"
    )
    cliente = models.CharField(max_length=255)
    comissao_bruta_escritorio = models.DecimalField(max_digits=14, decimal_places=2)
    comissao_assessor_60 = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='Campo "Comissão Assessor 60%" da origem — valor já líquido informado manualmente, não recalculado pelo sistema (suposição registrada na análise arquitetural).',
    )
    parcela = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"PJ2 Seguros — {self.get_seguradora_display()} — {self.cliente}"


class PlusEntry(BaseEntry):
    """Lançamento manual de Plus (seção 16). Sem import_batch."""

    class Parceiro(models.TextChoices):
        VIPMARES = "VIPMARES", "Vipmares"
        MD_GARANTIDOR = "MD_GARANTIDOR", "MD Garantidor"
        LMS_FOCUS = "LMS_FOCUS", "LMS/Focus"
        RODOBENS = "RODOBENS", "Rodobens"
        DUOPLAN = "DUOPLAN", "Duoplan"
        ESOLEN_FINEPE = "ESOLEN_FINEPE", "Esolen (Finepe)"
        PRIMO_PRECATORIOS = "PRIMO_PRECATORIOS", "Primo Precatórios"
        NEWAVE = "NEWAVE", "Newave"
        FINANC_SAFRA = "FINANC_SAFRA", "Financ Safra"
        ESSENCIAL = "ESSENCIAL", "Essencial"
        REAL_CRED = "REAL_CRED", "Real Cred"
        PREV = "PREV", "Prev"
        SORIA_CAPITAL = "SORIA_CAPITAL", "Soria Capital"
        BV_FINANCEIRA = "BV_FINANCEIRA", "BV Financeira"

    parceiro = models.CharField(max_length=30, choices=Parceiro.choices)
    produto = models.ForeignKey(
        "financial.Product", on_delete=models.PROTECT, related_name="plus_entries"
    )
    cliente = models.CharField(max_length=255, blank=True)

    valor_bruto = models.DecimalField(max_digits=14, decimal_places=2)
    percentual_imposto = models.DecimalField(max_digits=5, decimal_places=2)
    valor_imposto = models.DecimalField(max_digits=14, decimal_places=2)
    valor_liquido = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"Plus — {self.get_parceiro_display()} — {self.data_lancamento}"

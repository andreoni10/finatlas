from django.contrib import admin

from .models import Company, Product

from .models import Commission

from .models import PJ1Entry, PJ2PrevidenciaEntry, PJ2SegurosEntry, PlusEntry


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "organization", "ativo")
    list_filter = ("tipo", "organization", "ativo")
    search_fields = ("nome",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("nome", "company", "ativo")
    list_filter = ("company__organization", "ativo")
    search_fields = ("nome",)


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = (
        "advisor",
        "mes_referencia",
        "ano_referencia",
        "percentual",
        "organization",
    )
    list_filter = ("organization", "ano_referencia")
    search_fields = ("advisor__codigo_assessor", "advisor__user__username")


@admin.register(PJ1Entry)
class PJ1EntryAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_cliente",
        "advisor",
        "data_lancamento",
        "comissao_assessor_direto",
        "organization",
    )
    list_filter = ("organization", "ano_referencia", "mes_referencia")
    search_fields = ("codigo_cliente", "codigo_assessor_direto")


@admin.register(PJ2PrevidenciaEntry)
class PJ2PrevidenciaEntryAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_cliente",
        "advisor",
        "data_lancamento",
        "comissao_escritorio",
        "organization",
    )
    list_filter = ("organization", "ano_referencia", "mes_referencia")
    search_fields = ("codigo_cliente", "codigo_assessor")


@admin.register(PJ2SegurosEntry)
class PJ2SegurosEntryAdmin(admin.ModelAdmin):
    list_display = (
        "seguradora",
        "cliente",
        "advisor",
        "data_lancamento",
        "comissao_assessor_60",
        "organization",
    )
    list_filter = ("organization", "seguradora", "ano_referencia", "mes_referencia")
    search_fields = ("cliente",)


@admin.register(PlusEntry)
class PlusEntryAdmin(admin.ModelAdmin):
    list_display = (
        "parceiro",
        "cliente",
        "advisor",
        "data_lancamento",
        "valor_liquido",
        "organization",
    )
    list_filter = ("organization", "parceiro", "ano_referencia", "mes_referencia")
    search_fields = ("cliente",)

from django.contrib import admin

from .models import Company, Product

from .models import Commission


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

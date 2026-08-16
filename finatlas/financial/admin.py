from django.contrib import admin

from .models import Company, Product


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

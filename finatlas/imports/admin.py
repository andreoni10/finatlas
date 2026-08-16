from django.contrib import admin

from .models import ImportBatch


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("origem", "organization", "usuario", "criado_em")
    list_filter = ("origem", "organization")

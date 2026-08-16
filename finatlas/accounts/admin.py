from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AdvisorProfile, User


class AdvisorProfileInline(admin.StackedInline):
    model = AdvisorProfile
    can_delete = False
    fk_name = "user"
    extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [AdvisorProfileInline]
    list_display = ("username", "email", "role", "organization", "is_active")
    list_filter = ("role", "organization", "is_active")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("FinAtlas", {"fields": ("role", "organization")}),
    )

    def get_inline_instances(self, request, obj=None):
        # Só mostra o inline de AdvisorProfile quando o usuário já existe —
        # evita erro ao criar um usuário novo pelo admin.
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

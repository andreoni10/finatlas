from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin base para views restritas por papel (`role`).

    Uso: defina `allowed_roles = [User.Role.FINANCEIRO]` na view que
    herdar deste mixin.
    """

    allowed_roles: list[str] = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles


class OrganizationRequiredMixin(LoginRequiredMixin):
    """
    Garante que a view só opere dentro da organização do usuário logado.

    Views futuras (Financeiro, Assessor) devem usar
    `self.get_organization()` em vez de aceitar `organization_id` vindo
    de URL/POST — é isso que garante o isolamento entre organizações
    exigido na seção 10.1 do Prompt Master 2.0.
    """

    def get_organization(self):
        return self.request.user.organization

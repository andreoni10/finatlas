from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .mixins import RoleRequiredMixin
from .models import User


class FinAtlasLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def root_redirect(request):
    """
    View da raiz ('/'). Não autenticado -> login. Autenticado -> painel
    correspondente ao papel do usuário.
    """
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("post_login_redirect")


def post_login_redirect(request):
    """
    Ponto único de decisão de para onde o usuário vai após o login,
    baseado em `request.user.role`. É o LOGIN_REDIRECT_URL.
    """
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    if user.role == User.Role.SAAS_ADMIN:
        # DECISÃO: para o MVP, a administração do SaaS Admin é o próprio
        # admin do Django — não há necessidade de uma UI própria ainda.
        return redirect("/admin/")
    if user.role == User.Role.FINANCEIRO:
        return redirect("financeiro_home")
    if user.role == User.Role.ASSESSOR:
        return redirect("assessor_home")

    # SUPOSIÇÃO: um usuário sem role definido não deveria existir em
    # produção; em desenvolvimento, evitamos um erro 500 e voltamos ao login.
    return redirect("login")


class FinanceiroHomeView(RoleRequiredMixin, TemplateView):
    """Placeholder — será substituído pelo Dashboard Financeiro na Etapa 9."""

    template_name = "accounts/financeiro_home_placeholder.html"
    allowed_roles = [User.Role.FINANCEIRO]


class AssessorHomeView(RoleRequiredMixin, TemplateView):
    """Placeholder — será substituído pelo Dashboard do Assessor na Etapa 8."""

    template_name = "accounts/assessor_home_placeholder.html"
    allowed_roles = [User.Role.ASSESSOR]

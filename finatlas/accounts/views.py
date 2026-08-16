from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from .mixins import RoleRequiredMixin
from .models import User

from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .forms import AdvisorCreateForm, AdvisorUpdateForm
from .mixins import OrganizationRequiredMixin
from .models import AdvisorProfile


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


class FinanceiroBaseMixin(RoleRequiredMixin, OrganizationRequiredMixin):
    allowed_roles = [User.Role.FINANCEIRO]


class AdvisorListView(FinanceiroBaseMixin, ListView):
    model = AdvisorProfile
    template_name = "accounts/advisor_list.html"
    context_object_name = "advisors"

    def get_queryset(self):
        return AdvisorProfile.objects.filter(
            organization=self.get_organization()
        ).select_related("user")


class AdvisorCreateView(FinanceiroBaseMixin, View):
    template_name = "accounts/advisor_form.html"

    def get(self, request):
        form = AdvisorCreateForm(organization=self.get_organization())
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AdvisorCreateForm(request.POST, organization=self.get_organization())
        if form.is_valid():
            form.save()
            messages.success(request, "Assessor cadastrado com sucesso.")
            return redirect("advisor_list")
        return render(request, self.template_name, {"form": form})


class AdvisorUpdateView(FinanceiroBaseMixin, View):
    template_name = "accounts/advisor_form.html"

    def get_profile(self):
        # Restringe à organização do usuário — mesmo padrão de segurança
        # usado no CRUD de Company/Product da Etapa 2.
        return get_object_or_404(
            AdvisorProfile, pk=self.kwargs["pk"], organization=self.get_organization()
        )

    def get(self, request, pk):
        profile = self.get_profile()
        form = AdvisorUpdateForm(profile=profile)
        return render(request, self.template_name, {"form": form, "object": profile})

    def post(self, request, pk):
        profile = self.get_profile()
        form = AdvisorUpdateForm(request.POST, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Assessor atualizado com sucesso.")
            return redirect("advisor_list")
        return render(request, self.template_name, {"form": form, "object": profile})

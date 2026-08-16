from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from accounts.mixins import OrganizationRequiredMixin, RoleRequiredMixin
from accounts.models import User

from .forms import CompanyForm, ProductForm
from .models import Company, Product

from accounts.models import AdvisorProfile

from .forms import CommissionForm
from .models import Commission


class FinanceiroBaseMixin(RoleRequiredMixin, OrganizationRequiredMixin):
    """Combina restrição de papel (Financeiro) com escopo de organização."""

    allowed_roles = [User.Role.FINANCEIRO]


# ---------------------------------------------------------------- Company --


class CompanyListView(FinanceiroBaseMixin, ListView):
    model = Company
    template_name = "financial/company_list.html"
    context_object_name = "companies"

    def get_queryset(self):
        return Company.objects.filter(organization=self.get_organization())


class CompanyCreateView(FinanceiroBaseMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "financial/company_form.html"
    success_url = reverse_lazy("company_list")

    def form_valid(self, form):
        # A organização nunca vem do formulário — sempre do usuário logado.
        form.instance.organization = self.get_organization()
        messages.success(self.request, "Empresa cadastrada com sucesso.")
        return super().form_valid(form)


class CompanyUpdateView(FinanceiroBaseMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "financial/company_form.html"
    success_url = reverse_lazy("company_list")

    def get_queryset(self):
        # Restringe o objeto editável à organização do usuário: um
        # Financeiro da Organização A não consegue editar (nem por URL
        # manipulada) uma Company da Organização B — recebe 404.
        return Company.objects.filter(organization=self.get_organization())

    def form_valid(self, form):
        messages.success(self.request, "Empresa atualizada com sucesso.")
        return super().form_valid(form)


class CompanyToggleActiveView(FinanceiroBaseMixin, View):
    """Ativa/desativa uma Company (soft delete) — nunca exclusão física."""

    def post(self, request, pk):
        company = get_object_or_404(
            Company, pk=pk, organization=self.get_organization()
        )
        company.ativo = not company.ativo
        company.save(update_fields=["ativo"])
        messages.success(
            request,
            f"Empresa {'ativada' if company.ativo else 'desativada'} com sucesso.",
        )
        return redirect("company_list")


# ---------------------------------------------------------------- Product --


class ProductListView(FinanceiroBaseMixin, ListView):
    model = Product
    template_name = "financial/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(
            company__organization=self.get_organization()
        ).select_related("company")


class ProductCreateView(FinanceiroBaseMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "financial/product_form.html"
    success_url = reverse_lazy("product_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Produto cadastrado com sucesso.")
        return super().form_valid(form)


class ProductUpdateView(FinanceiroBaseMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "financial/product_form.html"
    success_url = reverse_lazy("product_list")

    def get_queryset(self):
        return Product.objects.filter(company__organization=self.get_organization())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Produto atualizado com sucesso.")
        return super().form_valid(form)


class ProductToggleActiveView(FinanceiroBaseMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(
            Product, pk=pk, company__organization=self.get_organization()
        )
        product.ativo = not product.ativo
        product.save(update_fields=["ativo"])
        messages.success(
            request,
            f"Produto {'ativado' if product.ativo else 'desativado'} com sucesso.",
        )
        return redirect("product_list")


class CommissionListView(FinanceiroBaseMixin, ListView):
    model = Commission
    template_name = "financial/commission_list.html"
    context_object_name = "commissions"

    def get_queryset(self):
        qs = Commission.objects.filter(
            organization=self.get_organization()
        ).select_related("advisor__user")
        advisor_id = self.request.GET.get("advisor")
        if advisor_id:
            qs = qs.filter(advisor_id=advisor_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["advisors"] = AdvisorProfile.objects.filter(
            organization=self.get_organization(), ativo=True
        )
        return context


class CommissionCreateView(FinanceiroBaseMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = "financial/commission_form.html"
    success_url = reverse_lazy("commission_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.get_organization()
        form.instance.criado_por = self.request.user
        messages.success(self.request, "Comissão cadastrada com sucesso.")
        return super().form_valid(form)


class CommissionUpdateView(FinanceiroBaseMixin, UpdateView):
    model = Commission
    form_class = CommissionForm
    template_name = "financial/commission_form.html"
    success_url = reverse_lazy("commission_list")

    def get_queryset(self):
        return Commission.objects.filter(organization=self.get_organization())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Comissão atualizada com sucesso.")
        return super().form_valid(form)

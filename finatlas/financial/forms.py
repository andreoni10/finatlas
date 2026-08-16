from django import forms

from .models import Company, Product

from accounts.models import AdvisorProfile

from .models import Commission

TAILWIND_INPUT = "w-full rounded-md border border-slate-300 px-3 py-2 focus:border-slate-500 focus:ring-slate-500"
TAILWIND_SELECT = TAILWIND_INPUT


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["nome", "tipo", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
            "tipo": forms.Select(attrs={"class": TAILWIND_SELECT}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["company", "nome", "ativo"]
        widgets = {
            "company": forms.Select(attrs={"class": TAILWIND_SELECT}),
            "nome": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        """
        `organization` é obrigatório e vem sempre da view (a partir de
        `request.user.organization`), nunca do formulário submetido pelo
        usuário. Isso impede que um Financeiro associe um produto a uma
        empresa de outra organização manipulando o HTML do <select>.
        """
        super().__init__(*args, **kwargs)
        if organization is not None:
            self.fields["company"].queryset = Company.objects.filter(
                organization=organization, ativo=True
            )


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ["advisor", "percentual", "mes_referencia", "ano_referencia"]
        widgets = {
            "advisor": forms.Select(attrs={"class": TAILWIND_SELECT}),
            "percentual": forms.NumberInput(
                attrs={"class": TAILWIND_INPUT, "step": "0.01"}
            ),
            "mes_referencia": forms.NumberInput(
                attrs={"class": TAILWIND_INPUT, "min": 1, "max": 12}
            ),
            "ano_referencia": forms.NumberInput(
                attrs={"class": TAILWIND_INPUT, "min": 2000}
            ),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        if organization is not None:
            # Só assessores ativos da própria organização podem receber
            # uma nova comissão.
            self.fields["advisor"].queryset = AdvisorProfile.objects.filter(
                organization=organization, ativo=True
            )

from django import forms

from .models import Company, Product

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

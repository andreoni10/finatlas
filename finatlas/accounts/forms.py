from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import AdvisorProfile, User

TAILWIND_INPUT = "w-full rounded-md border border-slate-300 px-3 py-2 focus:border-slate-500 focus:ring-slate-500"


class AdvisorCreateForm(forms.Form):
    """
    Cria um User (role=ASSESSOR) + AdvisorProfile em conjunto.

    A senha é definida pelo Financeiro no cadastro (MVP simples — sem
    fluxo de convite por e-mail, registrado em Evoluções Futuras).
    """

    username = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT})
    )
    first_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}),
    )
    email = forms.EmailField(
        required=False, widget=forms.EmailInput(attrs={"class": TAILWIND_INPUT})
    )
    codigo_assessor = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": TAILWIND_INPUT}),
        help_text="Senha inicial. O assessor pode alterá-la depois do primeiro login.",
    )

    def __init__(self, *args, organization=None, **kwargs):
        # `organization` vem sempre da view (request.user.organization),
        # nunca de um campo do formulário — impede que o Financeiro
        # crie um assessor em outra organização.
        self.organization = organization
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Já existe um usuário com este nome de usuário."
            )
        return username

    def clean_codigo_assessor(self):
        codigo = self.cleaned_data["codigo_assessor"]
        if AdvisorProfile.objects.filter(
            organization=self.organization, codigo_assessor=codigo
        ).exists():
            raise forms.ValidationError(
                "Já existe um assessor com este código nesta organização."
            )
        return codigo

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data.get("last_name", ""),
            email=self.cleaned_data.get("email", ""),
            password=self.cleaned_data["password"],
            role=User.Role.ASSESSOR,
            organization=self.organization,
        )
        return AdvisorProfile.objects.create(
            user=user,
            organization=self.organization,
            codigo_assessor=self.cleaned_data["codigo_assessor"],
        )


class AdvisorUpdateForm(forms.Form):
    """Edita dados cadastrais e status. Não altera senha nesta tela."""

    first_name = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}),
    )
    email = forms.EmailField(
        required=False, widget=forms.EmailInput(attrs={"class": TAILWIND_INPUT})
    )
    codigo_assessor = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT})
    )
    ativo = forms.BooleanField(required=False)

    def __init__(self, *args, profile=None, **kwargs):
        self.profile = profile
        super().__init__(*args, **kwargs)
        if profile is not None and not self.is_bound:
            self.initial.update(
                {
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "email": profile.user.email,
                    "codigo_assessor": profile.codigo_assessor,
                    "ativo": profile.ativo,
                }
            )

    def clean_codigo_assessor(self):
        codigo = self.cleaned_data["codigo_assessor"]
        qs = AdvisorProfile.objects.filter(
            organization=self.profile.organization, codigo_assessor=codigo
        ).exclude(pk=self.profile.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Já existe um assessor com este código nesta organização."
            )
        return codigo

    def save(self):
        user = self.profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data.get("last_name", "")
        user.email = self.cleaned_data.get("email", "")
        # Desativar o assessor desativa o User (bloqueia login) e o
        # AdvisorProfile (some das listagens do Financeiro) juntos.
        user.is_active = self.cleaned_data["ativo"]
        user.save(update_fields=["first_name", "last_name", "email", "is_active"])

        self.profile.codigo_assessor = self.cleaned_data["codigo_assessor"]
        self.profile.ativo = self.cleaned_data["ativo"]
        self.profile.save(update_fields=["codigo_assessor", "ativo"])
        return self.profile

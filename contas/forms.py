from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm

from .models import Endereco, Usuario


class CadastroForm(forms.ModelForm):
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    confirmacao = forms.CharField(
        label="Confirme a senha", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )
    aceite = forms.BooleanField(
        label="Concordo com o uso dos meus dados apenas para processar meus pedidos (LGPD).",
        error_messages={"required": "É preciso aceitar para criar a conta."},
    )

    class Meta:
        model = Usuario
        fields = ["nome", "email", "telefone"]
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "telefone": forms.TextInput(attrs={"inputmode": "tel", "placeholder": "(11) 99999-9999"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail. Tente entrar.")
        return email

    def clean(self):
        dados = super().clean()
        senha, conf = dados.get("senha"), dados.get("confirmacao")
        if senha and conf and senha != conf:
            self.add_error("confirmacao", "As senhas não conferem.")
        if senha:
            usuario_tmp = Usuario(email=dados.get("email", ""), nome=dados.get("nome", ""))
            try:
                password_validation.validate_password(senha, usuario_tmp)
            except forms.ValidationError as erro:
                self.add_error("senha", erro)
        return dados

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}))

    error_messages = {
        "invalid_login": "E-mail ou senha incorretos.",
        "inactive": "Esta conta está desativada.",
    }

    def clean_username(self):
        # O cadastro grava o e-mail em minúsculas; o celular costuma capitalizar a 1ª letra.
        return self.cleaned_data["username"].strip().lower()


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nome", "telefone"]


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ["apelido", "cep", "logradouro", "numero", "complemento", "bairro", "cidade", "principal"]
        widgets = {"cep": forms.TextInput(attrs={"inputmode": "numeric", "placeholder": "00000-000"})}
        labels = {"principal": "Usar como endereço principal"}

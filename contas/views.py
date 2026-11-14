from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CadastroForm, EnderecoForm, LoginForm, PerfilForm
from .models import Endereco


def destino_seguro(request, padrao: str) -> str:
    """Evita open redirect: só aceita `next` relativo ao próprio site."""
    destino = request.GET.get("next") or request.POST.get("next") or ""
    if destino and url_has_allowed_host_and_scheme(destino, {request.get_host()}, request.is_secure()):
        return destino
    return padrao


def cadastrar(request):
    """US01 – criar conta."""
    if request.user.is_authenticated:
        return redirect("catalogo:vitrine")
    form = CadastroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Bem-vindo(a), {usuario.nome.split()[0]}! Sua conta foi criada.")
        return redirect(destino_seguro(request, "/"))
    return render(request, "contas/cadastro.html", {"form": form})


class EntrarView(auth_views.LoginView):
    """US02 – login por e-mail e senha."""

    template_name = "contas/entrar.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, f"Olá, {self.request.user.nome.split()[0]}!")
        return resposta

    def get_default_redirect_url(self):
        if self.request.user.is_admin_loja:
            return "/painel/"
        return super().get_default_redirect_url()


class SairView(auth_views.LogoutView):
    def post(self, request, *args, **kwargs):
        resposta = super().post(request, *args, **kwargs)
        messages.info(request, "Você saiu da sua conta.")
        return resposta


@login_required
def perfil(request):
    """US03 – dados pessoais e endereços."""
    form = PerfilForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dados atualizados.")
        return redirect("contas:perfil")
    return render(request, "contas/perfil.html", {"form": form, "enderecos": request.user.enderecos.all()})


def _salvar_endereco(form, usuario):
    with transaction.atomic():
        endereco = form.save(commit=False)
        endereco.usuario = usuario
        primeiro = not usuario.enderecos.exclude(pk=endereco.pk).exists()
        if endereco.principal or primeiro:
            usuario.enderecos.exclude(pk=endereco.pk).update(principal=False)
            endereco.principal = True
        endereco.save()
    return endereco


@login_required
def endereco_form(request, pk=None):
    endereco = get_object_or_404(Endereco, pk=pk, usuario=request.user) if pk else None
    form = EnderecoForm(request.POST or None, instance=endereco)
    if request.method == "POST" and form.is_valid():
        _salvar_endereco(form, request.user)
        messages.success(request, "Endereço salvo.")
        return redirect(destino_seguro(request, "/conta/perfil/"))
    return render(
        request,
        "contas/endereco_form.html",
        {"form": form, "endereco": endereco, "voltar": destino_seguro(request, "/conta/perfil/")},
    )


@login_required
@require_POST
def endereco_excluir(request, pk):
    endereco = get_object_or_404(Endereco, pk=pk, usuario=request.user)
    era_principal = endereco.principal
    endereco.delete()
    if era_principal:
        outro = request.user.enderecos.first()
        if outro:
            outro.principal = True
            outro.save(update_fields=["principal"])
    messages.success(request, "Endereço removido.")
    return redirect("contas:perfil")

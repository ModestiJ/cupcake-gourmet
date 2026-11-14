"""Painel do administrador da loja (US07, US08, US12, US15). RN07: só perfil ADMIN."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalogo.models import Categoria, Produto
from contas.views import destino_seguro
from pedidos import services
from pedidos.models import Pedido, ZonaEntrega
from pedidos.views import montar_linha_do_tempo

from .forms import CategoriaForm, ProdutoForm, ZonaEntregaForm


def admin_requerido(view):
    @wraps(view)
    @login_required
    def _view(request, *args, **kwargs):
        if not request.user.is_admin_loja:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return _view


@admin_requerido
def inicio(request):
    filtro = request.GET.get("status", "abertos")
    pedidos = Pedido.objects.select_related("usuario", "pagamento").prefetch_related("itens")
    if filtro == "abertos":
        pedidos = pedidos.exclude(status__in=[Pedido.Status.ENTREGUE, Pedido.Status.CANCELADO]).order_by("criado_em")
    elif filtro in Pedido.Status.values:
        pedidos = pedidos.filter(status=filtro)
    pedidos = list(pedidos[:100])
    for p in pedidos:
        p.proximo = services.proximo_status(p)
        p.proximo_rotulo = Pedido.Status(p.proximo).label if p.proximo else ""
    return render(
        request,
        "painel/inicio.html",
        {
            "pedidos": pedidos,
            "resumo": services.resumo_vendas_do_dia(),
            "filtro": filtro,
            "status_choices": Pedido.Status.choices,
            "baixo_estoque": Produto.objects.filter(ativo=True, estoque__lte=5).order_by("estoque")[:6],
        },
    )


@admin_requerido
def pedido_detalhe(request, pk):
    pedido = get_object_or_404(Pedido.objects.select_related("usuario", "pagamento"), pk=pk)
    proximo = services.proximo_status(pedido)
    return render(
        request,
        "painel/pedido_detalhe.html",
        {
            "pedido": pedido,
            "itens": pedido.itens.all(),
            "linha_do_tempo": montar_linha_do_tempo(pedido),
            "proximo_rotulo": Pedido.Status(proximo).label if proximo else "",
        },
    )


@admin_requerido
@require_POST
def pedido_avancar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedido = services.avancar_status(pedido, request.user)
        messages.success(request, f"Pedido {pedido.codigo}: {pedido.get_status_display()}.")
    except services.ErroPedido as erro:
        messages.error(request, f"Pedido {pedido.codigo}: {erro}")
    return redirect(destino_seguro(request, "/painel/"))


@admin_requerido
@require_POST
def pedido_cancelar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        services.cancelar_pedido(pedido, request.user)
        messages.success(request, f"Pedido {pedido.codigo} cancelado e estoque devolvido.")
    except services.ErroPedido as erro:
        messages.error(request, str(erro))
    return redirect("painel:pedido_detalhe", pk=pk)


# --------------------------------------------------------------------------- #
# Cadastros genéricos (produtos, categorias, zonas)
# --------------------------------------------------------------------------- #
CADASTROS = {
    "produtos": (Produto, ProdutoForm, "cupcake", "Cupcakes"),
    "categorias": (Categoria, CategoriaForm, "categoria", "Categorias"),
    "zonas": (ZonaEntrega, ZonaEntregaForm, "zona de entrega", "Zonas de entrega"),
}


def _cadastro(tipo):
    if tipo not in CADASTROS:
        from django.http import Http404

        raise Http404
    return CADASTROS[tipo]


@admin_requerido
def lista(request, tipo):
    modelo, _, _, titulo = _cadastro(tipo)
    objetos = modelo.objects.all()
    if tipo == "produtos":
        objetos = objetos.select_related("categoria").order_by("categoria__ordem", "nome")
    return render(request, "painel/lista.html", {"objetos": objetos, "tipo": tipo, "titulo": titulo})


@admin_requerido
def formulario(request, tipo, pk=None):
    modelo, form_cls, nome, titulo = _cadastro(tipo)
    obj = get_object_or_404(modelo, pk=pk) if pk else None
    form = form_cls(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        salvo = form.save()
        messages.success(request, f"{nome.capitalize()} “{salvo}” salvo(a).")
        return redirect("painel:lista", tipo=tipo)
    return render(request, "painel/formulario.html", {"form": form, "obj": obj, "tipo": tipo, "nome": nome, "titulo": titulo})


@admin_requerido
@require_POST
def excluir(request, tipo, pk):
    modelo, _, nome, _ = _cadastro(tipo)
    obj = get_object_or_404(modelo, pk=pk)
    try:
        obj.delete()
        messages.success(request, f"{nome.capitalize()} excluído(a).")
    except ProtectedError:
        campo = "ativo" if hasattr(obj, "ativo") else "ativa"
        setattr(obj, campo, False)
        obj.save(update_fields=[campo])
        messages.warning(
            request, f"“{obj}” tem pedidos ou produtos vinculados; foi desativado(a) em vez de excluído(a)."
        )
    return redirect("painel:lista", tipo=tipo)

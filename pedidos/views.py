from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalogo.models import Produto
from contas.views import destino_seguro

from . import services
from .carrinho import Carrinho, ErroCarrinho
from .models import Pagamento, Pedido, ZonaEntrega
from .pagamento import GatewaySimulado, obter_gateway


def _quantidade(request, padrao=1) -> int:
    try:
        return int(request.POST.get("quantidade", padrao))
    except (TypeError, ValueError):
        return -1


# --------------------------------------------------------------------------- #
# Carrinho (US09)
# --------------------------------------------------------------------------- #
def carrinho_ver(request):
    carrinho = Carrinho(request.session)
    linhas = carrinho.linhas()
    subtotal = sum((l.total for l in linhas), 0)
    return render(request, "pedidos/carrinho.html", {"linhas": linhas, "subtotal": subtotal})


@require_POST
def carrinho_adicionar(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    try:
        Carrinho(request.session).adicionar(produto, _quantidade(request))
        messages.success(request, f"{produto.nome} adicionado ao carrinho.")
    except ErroCarrinho as erro:
        messages.error(request, str(erro))
    return redirect(destino_seguro(request, "/carrinho/"))


@require_POST
def carrinho_atualizar(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    try:
        Carrinho(request.session).atualizar(produto, _quantidade(request))
    except ErroCarrinho as erro:
        messages.error(request, str(erro))
    return redirect("pedidos:carrinho")


@require_POST
def carrinho_remover(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    Carrinho(request.session).remover(produto)
    messages.info(request, f"{produto.nome} removido do carrinho.")
    return redirect("pedidos:carrinho")


# --------------------------------------------------------------------------- #
# Checkout (US10, US13, US16)
# --------------------------------------------------------------------------- #
@login_required
def checkout(request):
    carrinho = Carrinho(request.session)
    linhas = carrinho.linhas()
    if not linhas:
        messages.info(request, "Seu carrinho está vazio.")
        return redirect("catalogo:vitrine")

    enderecos = list(request.user.enderecos.all())
    zonas = {z.bairro.lower(): z.taxa for z in ZonaEntrega.objects.filter(ativa=True)}
    for e in enderecos:
        e.taxa = zonas.get(e.bairro.lower())  # None = bairro não atendido

    if request.method == "POST":
        tipo = request.POST.get("tipo_entrega", "")
        metodo = request.POST.get("metodo_pagamento", "")
        endereco = None
        if tipo == Pedido.Tipo.ENTREGA:
            endereco = next((e for e in enderecos if str(e.pk) == request.POST.get("endereco")), None)
        try:
            pedido = services.criar_pedido(
                request.user, carrinho, tipo, metodo, endereco, request.POST.get("observacao", "")
            )
        except services.ErroPedido as erro:
            messages.error(request, str(erro))
        else:
            messages.success(request, f"Pedido {pedido.codigo} recebido!")
            if metodo == Pagamento.Metodo.NA_ENTREGA:
                return redirect("pedidos:detalhe", pk=pedido.pk)
            return redirect("pedidos:pagamento", pk=pedido.pk)

    subtotal = sum((l.total for l in linhas), 0)
    return render(
        request,
        "pedidos/checkout.html",
        {
            "linhas": linhas,
            "subtotal": subtotal,
            "enderecos": enderecos,
            "metodos": Pagamento.Metodo.choices,
            "post": request.POST,
        },
    )


def _pedido_do_usuario(request, pk) -> Pedido:
    """RN07: cliente só acessa os próprios pedidos (404 para os demais)."""
    pedido = get_object_or_404(Pedido.objects.select_related("pagamento"), pk=pk)
    if pedido.usuario_id != request.user.pk:
        raise Http404
    return pedido


@login_required
def pagamento(request, pk):
    """US14 – pagamento simulado (Pix ou cartão)."""
    pedido = _pedido_do_usuario(request, pk)
    pag = pedido.pagamento
    if request.method == "POST":
        try:
            gateway = GatewaySimulado(recusar=True) if request.POST.get("simular") == "recusa" else None
            resultado = services.pagar_pedido(pedido, gateway)
        except services.ErroPedido as erro:
            messages.error(request, str(erro))
            return redirect("pedidos:detalhe", pk=pk)
        if resultado.aprovado:
            messages.success(request, "Pagamento aprovado! Já vamos preparar seus cupcakes.")
            return redirect("pedidos:detalhe", pk=pk)
        messages.error(request, f"{resultado.mensagem} Tente novamente ou escolha outra forma.")
        return redirect("pedidos:pagamento", pk=pk)

    if pag.status == Pagamento.Status.APROVADO or pag.metodo == Pagamento.Metodo.NA_ENTREGA or pedido.status == Pedido.Status.CANCELADO:
        return redirect("pedidos:detalhe", pk=pk)
    codigo_pix = obter_gateway().codigo_pix(pag.valor, pedido.codigo) if pag.metodo == Pagamento.Metodo.PIX else ""
    return render(request, "pedidos/pagamento.html", {"pedido": pedido, "pag": pag, "codigo_pix": codigo_pix})


# --------------------------------------------------------------------------- #
# Acompanhamento (US11, US17)
# --------------------------------------------------------------------------- #
@login_required
def meus_pedidos(request):
    pedidos = request.user.pedidos.select_related("pagamento").prefetch_related("itens")
    return render(request, "pedidos/meus_pedidos.html", {"pedidos": pedidos})


ETAPAS_ENTREGA = [Pedido.Status.RECEBIDO, Pedido.Status.EM_PREPARO, Pedido.Status.SAIU_PARA_ENTREGA, Pedido.Status.ENTREGUE]
ETAPAS_RETIRADA = [Pedido.Status.RECEBIDO, Pedido.Status.EM_PREPARO, Pedido.Status.PRONTO_RETIRADA, Pedido.Status.ENTREGUE]


def montar_linha_do_tempo(pedido: Pedido) -> list[dict]:
    feitos = {h.status: h.alterado_em for h in pedido.historico.all()}
    etapas = ETAPAS_ENTREGA if pedido.tipo_entrega == Pedido.Tipo.ENTREGA else ETAPAS_RETIRADA
    linha = [{"rotulo": Pedido.Status(s).label, "quando": feitos.get(s), "feito": s in feitos} for s in etapas]
    if Pedido.Status.CANCELADO in feitos:
        linha = [e for e in linha if e["feito"]]
        linha.append({"rotulo": "Cancelado", "quando": feitos[Pedido.Status.CANCELADO], "feito": True, "cancelado": True})
    return linha


@login_required
def detalhe(request, pk):
    pedido = _pedido_do_usuario(request, pk)
    return render(
        request,
        "pedidos/detalhe.html",
        {
            "pedido": pedido,
            "itens": pedido.itens.all(),
            "linha_do_tempo": montar_linha_do_tempo(pedido),
            "pode_cancelar": pedido.status == Pedido.Status.RECEBIDO,
            "pode_pagar": pedido.pagamento.metodo != Pagamento.Metodo.NA_ENTREGA
            and pedido.pagamento.status in (Pagamento.Status.PENDENTE, Pagamento.Status.RECUSADO)
            and pedido.status != Pedido.Status.CANCELADO,
        },
    )


@login_required
@require_POST
def cancelar(request, pk):
    pedido = _pedido_do_usuario(request, pk)
    try:
        services.cancelar_pedido(pedido, request.user)
        messages.success(request, f"Pedido {pedido.codigo} cancelado.")
    except services.ErroPedido as erro:
        messages.error(request, str(erro))
    return redirect("pedidos:detalhe", pk=pk)


def areas_entrega(request):
    """US16 – consulta pública de bairros atendidos e taxas."""
    return render(request, "pedidos/areas_entrega.html", {"zonas": ZonaEntrega.objects.filter(ativa=True)})

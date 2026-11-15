"""Regras de negócio de pedidos (RN01–RN08).

Views (controllers) chamam estas funções; elas não conhecem HTTP. Isso
permite testá-las unitariamente e reaproveitá-las (ex.: futura API mobile).
"""
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, F, Sum
from django.utils import timezone

from catalogo.models import Produto
from catalogo.texto import normalizar
from contas.models import Endereco, Usuario

from .carrinho import Carrinho
from .models import HistoricoStatus, Pagamento, Pedido, ZonaEntrega
from .pagamento import GatewayPagamento, ResultadoCobranca, obter_gateway

S = Pedido.Status


class ErroPedido(Exception):
    """Violação de regra de negócio; a mensagem é exibida ao usuário."""


# --------------------------------------------------------------------------- #
# Entrega (RN05)
# --------------------------------------------------------------------------- #
def taxas_por_bairro() -> dict[str, Decimal]:
    """Zonas ativas indexadas pelo bairro normalizado ("São Paulo" = "sao paulo")."""
    return {normalizar(z.bairro): z.taxa for z in ZonaEntrega.objects.filter(ativa=True)}


def buscar_zona(bairro: str) -> ZonaEntrega | None:
    alvo = normalizar(bairro)
    return next((z for z in ZonaEntrega.objects.filter(ativa=True) if normalizar(z.bairro) == alvo), None)


def calcular_taxa(tipo_entrega: str, bairro: str | None) -> Decimal:
    if tipo_entrega == Pedido.Tipo.RETIRADA:
        return Decimal("0.00")
    if not bairro:
        raise ErroPedido("Informe o endereço de entrega.")
    zona = buscar_zona(bairro)
    if zona is None:
        raise ErroPedido(f"Ainda não entregamos no bairro {bairro}. Escolha retirada na loja.")
    return zona.taxa


# --------------------------------------------------------------------------- #
# Criação do pedido (US10, RN01, RN02, RN06)
# --------------------------------------------------------------------------- #
@transaction.atomic
def criar_pedido(
    usuario: Usuario,
    carrinho: Carrinho,
    tipo_entrega: str,
    metodo_pagamento: str,
    endereco: Endereco | None = None,
    observacao: str = "",
) -> Pedido:
    linhas = carrinho.linhas()
    if not linhas:
        raise ErroPedido("Seu carrinho está vazio.")
    if tipo_entrega not in Pedido.Tipo.values:
        raise ErroPedido("Tipo de entrega inválido.")
    if metodo_pagamento not in Pagamento.Metodo.values:
        raise ErroPedido("Forma de pagamento inválida.")
    if tipo_entrega == Pedido.Tipo.ENTREGA:
        if endereco is None:
            raise ErroPedido("Escolha um endereço para entrega.")
        if endereco.usuario_id != usuario.pk:
            raise ErroPedido("Endereço inválido.")

    taxa = calcular_taxa(tipo_entrega, endereco.bairro if endereco else None)

    # Trava as linhas de produto para evitar venda acima do estoque em pedidos concorrentes.
    ids = [l.produto.pk for l in linhas]
    produtos = {
        p.pk: p
        for p in Produto.objects.select_for_update(of=("self",)).select_related("categoria").filter(pk__in=ids)
    }

    pedido = Pedido.objects.create(
        usuario=usuario,
        tipo_entrega=tipo_entrega,
        endereco_entrega=str(endereco) if endereco and tipo_entrega == Pedido.Tipo.ENTREGA else "",
        bairro=endereco.bairro if endereco and tipo_entrega == Pedido.Tipo.ENTREGA else "",
        taxa_entrega=taxa,
        observacao=observacao.strip()[:300],
    )
    subtotal = Decimal("0")
    for linha in linhas:
        produto = produtos[linha.produto.pk]
        if not produto.disponivel or produto.estoque < linha.quantidade:
            raise ErroPedido(f"{produto.nome} acabou de esgotar. Ajuste seu carrinho.")
        pedido.itens.create(
            produto=produto,
            nome_produto=produto.nome,
            quantidade=linha.quantidade,
            preco_unitario=produto.preco,  # RN02: preço congelado
        )
        Produto.objects.filter(pk=produto.pk).update(estoque=F("estoque") - linha.quantidade)
        subtotal += produto.preco * linha.quantidade

    pedido.subtotal = subtotal
    pedido.total = subtotal + taxa
    pedido.save(update_fields=["subtotal", "total"])
    Pagamento.objects.create(pedido=pedido, metodo=metodo_pagamento, valor=pedido.total)
    HistoricoStatus.objects.create(pedido=pedido, status=S.RECEBIDO, alterado_por=usuario)
    carrinho.limpar()
    return pedido


# --------------------------------------------------------------------------- #
# Pagamento (US14)
# --------------------------------------------------------------------------- #
@transaction.atomic
def pagar_pedido(pedido: Pedido, gateway: GatewayPagamento | None = None) -> ResultadoCobranca:
    gateway = gateway or obter_gateway()
    pagamento = Pagamento.objects.select_for_update().get(pedido=pedido)
    if pedido.status == S.CANCELADO:
        raise ErroPedido("Este pedido foi cancelado.")
    if pagamento.metodo == Pagamento.Metodo.NA_ENTREGA:
        raise ErroPedido("Este pedido será pago na entrega/retirada.")
    if pagamento.status == Pagamento.Status.APROVADO:
        raise ErroPedido("Este pedido já está pago.")

    resultado = gateway.cobrar(pagamento.valor, pagamento.metodo, pedido.codigo)
    pagamento.transacao_ref = resultado.transacao_ref
    if resultado.aprovado:
        pagamento.status = Pagamento.Status.APROVADO
        pagamento.pago_em = timezone.now()
    else:
        pagamento.status = Pagamento.Status.RECUSADO
    pagamento.save()
    return resultado


# --------------------------------------------------------------------------- #
# Ciclo de vida do pedido (RN03, RN04, RN08)
# --------------------------------------------------------------------------- #
def proximo_status(pedido: Pedido) -> str | None:
    if pedido.status == S.RECEBIDO:
        return S.EM_PREPARO
    if pedido.status == S.EM_PREPARO:
        return S.SAIU_PARA_ENTREGA if pedido.tipo_entrega == Pedido.Tipo.ENTREGA else S.PRONTO_RETIRADA
    if pedido.status in (S.SAIU_PARA_ENTREGA, S.PRONTO_RETIRADA):
        return S.ENTREGUE
    return None


@transaction.atomic
def avancar_status(pedido: Pedido, admin: Usuario) -> Pedido:
    if not admin.is_admin_loja:
        raise ErroPedido("Apenas administradores podem alterar o status.")
    # of=("self",): o Postgres não trava o lado anulável do LEFT JOIN com pagamento.
    pedido = Pedido.objects.select_for_update(of=("self",)).select_related("pagamento").get(pk=pedido.pk)
    novo = proximo_status(pedido)
    if novo is None:
        raise ErroPedido(f"O pedido já está {pedido.get_status_display().lower()}.")
    if novo == S.EM_PREPARO and not pedido.pagamento.liberado_para_preparo:
        raise ErroPedido("Aguardando confirmação do pagamento para iniciar o preparo.")
    pedido.status = novo
    pedido.save(update_fields=["status", "atualizado_em"])
    if novo == S.ENTREGUE and pedido.pagamento.metodo == Pagamento.Metodo.NA_ENTREGA:
        pedido.pagamento.status = Pagamento.Status.APROVADO
        pedido.pagamento.pago_em = timezone.now()
        pedido.pagamento.save()
    HistoricoStatus.objects.create(pedido=pedido, status=novo, alterado_por=admin)
    return pedido


@transaction.atomic
def cancelar_pedido(pedido: Pedido, usuario: Usuario, gateway: GatewayPagamento | None = None) -> Pedido:
    gateway = gateway or obter_gateway()
    pedido = Pedido.objects.select_for_update(of=("self",)).select_related("pagamento").get(pk=pedido.pk)
    if usuario.is_admin_loja:
        if pedido.finalizado:
            raise ErroPedido("Pedido finalizado não pode ser cancelado.")
    else:
        if pedido.usuario_id != usuario.pk:
            raise ErroPedido("Pedido não encontrado.")
        if pedido.status != S.RECEBIDO:
            raise ErroPedido("O pedido já está em preparo e não pode mais ser cancelado. Fale com a loja.")

    for item in pedido.itens.all():  # devolve o estoque
        Produto.objects.filter(pk=item.produto_id).update(estoque=F("estoque") + item.quantidade)
    pag = pedido.pagamento
    if pag.status == Pagamento.Status.APROVADO and gateway.estornar(pag.transacao_ref):
        pag.status = Pagamento.Status.ESTORNADO
        pag.save(update_fields=["status"])
    pedido.status = S.CANCELADO
    pedido.save(update_fields=["status", "atualizado_em"])
    HistoricoStatus.objects.create(pedido=pedido, status=S.CANCELADO, alterado_por=usuario)
    return pedido


# --------------------------------------------------------------------------- #
# Indicadores (US15)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ResumoVendas:
    pedidos: int
    faturamento: Decimal
    ticket_medio: Decimal
    em_aberto: int


def resumo_vendas_do_dia(data=None) -> ResumoVendas:
    data = data or timezone.localdate()
    do_dia = Pedido.objects.filter(criado_em__date=data).exclude(status=S.CANCELADO)
    agg = do_dia.aggregate(n=Count("id"), soma=Sum("total"))
    n, soma = agg["n"] or 0, agg["soma"] or Decimal("0")
    em_aberto = Pedido.objects.exclude(status__in=[S.ENTREGUE, S.CANCELADO]).count()
    ticket = (soma / n).quantize(Decimal("0.01")) if n else Decimal("0.00")
    return ResumoVendas(pedidos=n, faturamento=soma, ticket_medio=ticket, em_aberto=em_aberto)

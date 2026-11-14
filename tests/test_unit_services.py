"""Testes unitários das regras de negócio de pedidos (RN02–RN08)."""
from decimal import Decimal

import pytest
from django.db import IntegrityError

from catalogo.models import Produto
from pedidos import services
from pedidos.models import Pagamento, Pedido
from pedidos.pagamento import GatewaySimulado, ResultadoCobranca

pytestmark = pytest.mark.unitario
S = Pedido.Status


class GatewayRecusa(GatewaySimulado):
    def cobrar(self, valor, metodo, referencia):
        return ResultadoCobranca(False, "X", "Recusado")


def test_resultado_e_imutavel():
    r = ResultadoCobranca(True, "a", "b")
    with pytest.raises(AttributeError):
        r.aprovado = False


def _pedido(cliente, carrinho, produto, endereco=None, tipo="ENTREGA", metodo="PIX", qtd=2):
    carrinho.adicionar(produto, qtd)
    return services.criar_pedido(cliente, carrinho, tipo, metodo, endereco)


# ---------------- taxa de entrega (RN05) ----------------
def test_taxa_retirada_e_zero(db):
    assert services.calcular_taxa("RETIRADA", None) == Decimal("0.00")


def test_taxa_por_bairro_ignora_maiusculas(zona):
    assert services.calcular_taxa("ENTREGA", "  centro ") == Decimal("5.00")


def test_bairro_nao_atendido(db):
    with pytest.raises(services.ErroPedido, match="Ainda não entregamos"):
        services.calcular_taxa("ENTREGA", "Longe")


# ---------------- criação do pedido ----------------
def test_cria_pedido_com_totais_estoque_e_historico(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    assert pedido.subtotal == Decimal("20.00")
    assert pedido.taxa_entrega == Decimal("5.00")
    assert pedido.total == Decimal("25.00")
    assert pedido.pagamento.valor == Decimal("25.00")
    assert pedido.pagamento.status == Pagamento.Status.PENDENTE
    assert pedido.historico.get().status == S.RECEBIDO
    assert pedido.bairro == "Centro"
    produto.refresh_from_db()
    assert produto.estoque == 8
    assert len(carrinho) == 0  # carrinho esvaziado


def test_preco_congelado_no_item_rn02(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    Produto.objects.filter(pk=produto.pk).update(preco=Decimal("99.00"))
    item = pedido.itens.get()
    assert item.preco_unitario == Decimal("10.00")
    assert item.total == Decimal("20.00")


def test_retirada_nao_cobra_taxa_e_nao_guarda_endereco(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco, tipo="RETIRADA")
    assert pedido.taxa_entrega == 0
    assert pedido.endereco_entrega == ""


def test_carrinho_vazio(cliente, carrinho):
    with pytest.raises(services.ErroPedido, match="vazio"):
        services.criar_pedido(cliente, carrinho, "RETIRADA", "PIX")


def test_entrega_exige_endereco(cliente, carrinho, produto):
    carrinho.adicionar(produto)
    with pytest.raises(services.ErroPedido, match="endereço"):
        services.criar_pedido(cliente, carrinho, "ENTREGA", "PIX", None)


def test_endereco_de_outro_usuario_e_rejeitado(outro_cliente, carrinho, produto, endereco):
    carrinho.adicionar(produto)
    with pytest.raises(services.ErroPedido, match="Endereço inválido"):
        services.criar_pedido(outro_cliente, carrinho, "ENTREGA", "PIX", endereco)


def test_entrega_em_bairro_nao_atendido(cliente, carrinho, produto, endereco_fora):
    carrinho.adicionar(produto)
    with pytest.raises(services.ErroPedido, match="Ainda não entregamos"):
        services.criar_pedido(cliente, carrinho, "ENTREGA", "PIX", endereco_fora)
    assert Pedido.objects.count() == 0


@pytest.mark.parametrize("tipo,metodo", [("VOO", "PIX"), ("RETIRADA", "BITCOIN")])
def test_tipo_ou_metodo_invalidos(cliente, carrinho, produto, tipo, metodo):
    carrinho.adicionar(produto)
    with pytest.raises(services.ErroPedido):
        services.criar_pedido(cliente, carrinho, tipo, metodo)


def test_esgotou_entre_carrinho_e_checkout_faz_rollback(cliente, carrinho, produto, produto2):
    carrinho.adicionar(produto, 2)
    carrinho.adicionar(produto2, 3)
    Produto.objects.filter(pk=produto2.pk).update(estoque=1)  # outro cliente comprou
    with pytest.raises(services.ErroPedido, match="acabou de esgotar"):
        services.criar_pedido(cliente, carrinho, "RETIRADA", "PIX")
    produto.refresh_from_db()
    assert produto.estoque == 10  # transação desfeita
    assert Pedido.objects.count() == 0


# ---------------- pagamento (US14) ----------------
def test_pagamento_aprovado(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    resultado = services.pagar_pedido(pedido)
    pedido.pagamento.refresh_from_db()
    assert resultado.aprovado
    assert pedido.pagamento.status == Pagamento.Status.APROVADO
    assert pedido.pagamento.pago_em is not None
    assert pedido.pagamento.transacao_ref.startswith("SIM-PIX-")


def test_pagamento_recusado(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    resultado = services.pagar_pedido(pedido, GatewayRecusa())
    pedido.pagamento.refresh_from_db()
    assert not resultado.aprovado
    assert pedido.pagamento.status == Pagamento.Status.RECUSADO


def test_gateway_simulado_aprova_recusa_e_valida_valor():
    assert GatewaySimulado().cobrar(Decimal("40.00"), "CARTAO", "#1").aprovado
    assert not GatewaySimulado(recusar=True).cobrar(Decimal("40.00"), "CARTAO", "#1").aprovado
    assert not GatewaySimulado().cobrar(Decimal("0"), "CARTAO", "#1").aprovado
    assert GatewaySimulado().estornar("REF") and not GatewaySimulado().estornar("")
    assert "PIXSIMULADO" in GatewaySimulado().codigo_pix(Decimal("10"), "#1")


def test_nao_paga_duas_vezes(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    services.pagar_pedido(pedido)
    with pytest.raises(services.ErroPedido, match="já está pago"):
        services.pagar_pedido(pedido)


def test_pagamento_na_entrega_nao_e_cobrado_online(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco, metodo="NA_ENTREGA")
    with pytest.raises(services.ErroPedido, match="na entrega"):
        services.pagar_pedido(pedido)


# ---------------- ciclo de vida (RN03, RN04, RN08) ----------------
def test_fluxo_completo_entrega(cliente, admin, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    services.pagar_pedido(pedido)
    for esperado in (S.EM_PREPARO, S.SAIU_PARA_ENTREGA, S.ENTREGUE):
        pedido = services.avancar_status(pedido, admin)
        assert pedido.status == esperado
    assert list(pedido.historico.values_list("status", flat=True)) == [
        S.RECEBIDO, S.EM_PREPARO, S.SAIU_PARA_ENTREGA, S.ENTREGUE
    ]
    with pytest.raises(services.ErroPedido, match="já está entregue"):
        services.avancar_status(pedido, admin)


def test_fluxo_retirada_usa_pronto_para_retirada(cliente, admin, carrinho, produto):
    pedido = _pedido(cliente, carrinho, produto, tipo="RETIRADA", metodo="NA_ENTREGA")
    services.avancar_status(pedido, admin)
    pedido = services.avancar_status(pedido, admin)
    assert pedido.status == S.PRONTO_RETIRADA


def test_rn08_nao_prepara_sem_pagamento_online(cliente, admin, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco, metodo="PIX")
    with pytest.raises(services.ErroPedido, match="Aguardando confirmação do pagamento"):
        services.avancar_status(pedido, admin)


def test_pagamento_na_entrega_e_aprovado_ao_entregar(cliente, admin, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco, metodo="NA_ENTREGA")
    for _ in range(3):
        pedido = services.avancar_status(pedido, admin)
    pedido.pagamento.refresh_from_db()
    assert pedido.pagamento.status == Pagamento.Status.APROVADO


def test_cliente_nao_avanca_status(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    with pytest.raises(services.ErroPedido, match="Apenas administradores"):
        services.avancar_status(pedido, cliente)


def test_cliente_cancela_recebido_e_estoque_volta(cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco, qtd=3)
    services.pagar_pedido(pedido)
    pedido = services.cancelar_pedido(pedido, cliente)
    produto.refresh_from_db()
    pedido.pagamento.refresh_from_db()
    assert pedido.status == S.CANCELADO
    assert produto.estoque == 10
    assert pedido.pagamento.status == Pagamento.Status.ESTORNADO


def test_cliente_nao_cancela_em_preparo_rn04(cliente, admin, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco, metodo="NA_ENTREGA")
    services.avancar_status(pedido, admin)
    with pytest.raises(services.ErroPedido, match="já está em preparo"):
        services.cancelar_pedido(pedido, cliente)


def test_cliente_nao_cancela_pedido_alheio(cliente, outro_cliente, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco)
    with pytest.raises(services.ErroPedido, match="não encontrado"):
        services.cancelar_pedido(pedido, outro_cliente)


def test_admin_cancela_em_preparo_mas_nao_finalizado(cliente, admin, carrinho, produto, endereco):
    pedido = _pedido(cliente, carrinho, produto, endereco, metodo="NA_ENTREGA")
    services.avancar_status(pedido, admin)
    assert services.cancelar_pedido(pedido, admin).status == S.CANCELADO
    with pytest.raises(services.ErroPedido, match="finalizado"):
        services.cancelar_pedido(pedido, admin)


# ---------------- indicadores (US15) ----------------
def test_resumo_vendas_ignora_cancelados(cliente, carrinho, produto, produto2, endereco):
    p1 = _pedido(cliente, carrinho, produto, endereco)  # 25,00
    _pedido(cliente, carrinho, produto2, None, tipo="RETIRADA", qtd=2)  # 25,00
    services.cancelar_pedido(p1, cliente)
    r = services.resumo_vendas_do_dia()
    assert (r.pedidos, r.faturamento, r.ticket_medio, r.em_aberto) == (1, Decimal("25.00"), Decimal("25.00"), 1)


def test_resumo_sem_vendas(db):
    r = services.resumo_vendas_do_dia()
    assert r.pedidos == 0 and r.ticket_medio == Decimal("0.00")


# ---------------- integridade no banco (RNF08) ----------------
def test_banco_rejeita_preco_zero(categoria):
    with pytest.raises(IntegrityError):
        Produto.objects.create(categoria=categoria, nome="Grátis", descricao="x", preco=Decimal("0"), estoque=1)


def test_banco_rejeita_retirada_com_taxa(cliente):
    with pytest.raises(IntegrityError):
        Pedido.objects.create(usuario=cliente, tipo_entrega="RETIRADA", taxa_entrega=Decimal("5"))

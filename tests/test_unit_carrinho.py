"""Testes unitários do carrinho (US09, RN01, RN06)."""
from decimal import Decimal

import pytest

from pedidos.carrinho import QTD_MAXIMA_POR_ITEM, ErroCarrinho

pytestmark = pytest.mark.unitario


def test_adicionar_soma_quantidades_e_calcula_subtotal(carrinho, produto, produto2):
    carrinho.adicionar(produto, 2)
    carrinho.adicionar(produto, 1)
    carrinho.adicionar(produto2, 2)
    assert carrinho.quantidade_total == 5
    assert carrinho.subtotal() == Decimal("55.00")  # 3*10 + 2*12.50


def test_nao_adiciona_produto_inativo(carrinho, produto):
    produto.ativo = False
    produto.save()
    with pytest.raises(ErroCarrinho, match="não está disponível"):
        carrinho.adicionar(produto)


def test_nao_adiciona_produto_de_categoria_inativa(carrinho, produto):
    produto.categoria.ativa = False
    produto.categoria.save()
    with pytest.raises(ErroCarrinho):
        carrinho.adicionar(produto)


def test_nao_ultrapassa_estoque(carrinho, produto):
    with pytest.raises(ErroCarrinho, match="Só temos 10"):
        carrinho.adicionar(produto, 11)


def test_quantidade_invalida(carrinho, produto):
    with pytest.raises(ErroCarrinho):
        carrinho.adicionar(produto, 0)


def test_limite_maximo_por_item(carrinho, produto):
    produto.estoque = 500
    produto.save()
    with pytest.raises(ErroCarrinho, match="Máximo"):
        carrinho.atualizar(produto, QTD_MAXIMA_POR_ITEM + 1)


def test_atualizar_para_zero_remove(carrinho, produto):
    carrinho.adicionar(produto, 2)
    carrinho.atualizar(produto, 0)
    assert len(carrinho) == 0


def test_item_que_ficou_indisponivel_sai_do_carrinho(carrinho, produto, produto2):
    carrinho.adicionar(produto, 1)
    carrinho.adicionar(produto2, 1)
    produto2.ativo = False
    produto2.save()
    linhas = carrinho.linhas()
    assert [l.produto.nome for l in linhas] == ["Morango"]
    assert len(carrinho) == 1


def test_preco_vem_sempre_do_banco(carrinho, produto):
    carrinho.adicionar(produto, 2)
    produto.preco = Decimal("11.00")
    produto.save()
    assert carrinho.subtotal() == Decimal("22.00")

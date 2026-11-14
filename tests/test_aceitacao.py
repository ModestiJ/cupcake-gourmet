"""Testes de aceitação – cenários Gherkin derivados das histórias do PIT I.

Cada teste percorre a aplicação como o usuário faria (cliente HTTP), do
início ao fim de uma história. Os IDs (USxx) batem com docs/situacao-1/requisitos.md.
"""
import pytest
from django.urls import reverse

from pedidos.models import Pedido

pytestmark = pytest.mark.aceitacao


def test_us01_us02_visitante_cria_conta_e_entra(client, db):
    """
    Dado que sou um visitante sem conta
    Quando preencho o cadastro com dados válidos e aceito a política de dados
    Então minha conta é criada, estou logado e consigo sair e entrar novamente
    """
    dados = {"nome": "Rita", "email": "rita@t.com", "senha": "Cupcake#2026", "confirmacao": "Cupcake#2026", "aceite": "on"}
    r = client.post(reverse("contas:cadastro"), dados, follow=True)
    assert "Bem-vindo(a), Rita" in r.content.decode()
    client.post(reverse("contas:sair"))
    r = client.post(reverse("contas:entrar"), {"username": "rita@t.com", "password": "Cupcake#2026"}, follow=True)
    assert "Olá, Rita" in r.content.decode()


def test_us04_us05_us09_cliente_navega_e_monta_carrinho(client, produto, produto2):
    """
    Dado que estou na vitrine
    Quando filtro pela categoria, abro o detalhe de um cupcake e adiciono 2 unidades
    Então o carrinho mostra o item com o subtotal correto
    """
    r = client.get(reverse("catalogo:vitrine"), {"categoria": produto.categoria.slug})
    assert produto.nome in r.content.decode()
    r = client.get(reverse("catalogo:detalhe", args=[produto.pk]))
    assert "R$ 10,00" in r.content.decode()
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 2})
    r = client.get(reverse("pedidos:carrinho"))
    assert "R$ 20,00" in r.content.decode()


def test_us10_us13_us14_us16_us17_compra_com_entrega_ate_a_entrega(client, cliente, admin, produto, endereco):
    """
    Dado que sou cliente logado com endereço em bairro atendido e tenho itens no carrinho
    Quando escolho entrega, pago via Pix e a loja avança o pedido até a entrega
    Então vejo a taxa do bairro no total e a linha do tempo completa do pedido
    """
    client.force_login(cliente)
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 2})
    r = client.post(reverse("pedidos:checkout"), {"tipo_entrega": "ENTREGA", "endereco": endereco.pk, "metodo_pagamento": "PIX"}, follow=True)
    pedido = Pedido.objects.get()
    assert pedido.total == 25  # 2 x 10,00 + taxa 5,00 (Centro)
    assert "Pix copia e cola" in r.content.decode()
    client.post(reverse("pedidos:pagamento", args=[pedido.pk]))

    client.force_login(admin)
    for _ in range(3):
        client.post(reverse("painel:pedido_avancar", args=[pedido.pk]))

    client.force_login(cliente)
    html = client.get(reverse("pedidos:detalhe", args=[pedido.pk])).content.decode()
    for etapa in ["Recebido", "Em preparo", "Saiu para entrega", "Entregue"]:
        assert etapa in html
    assert "Aprovado" in html


def test_us11_rn04_cliente_cancela_pedido_recebido(client, cliente, produto):
    """
    Dado que fiz um pedido para retirada que ainda não entrou em preparo
    Quando cancelo pelo histórico de pedidos
    Então o pedido aparece como cancelado e o estoque volta
    """
    client.force_login(cliente)
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 4})
    client.post(reverse("pedidos:checkout"), {"tipo_entrega": "RETIRADA", "metodo_pagamento": "NA_ENTREGA"})
    pedido = Pedido.objects.get()
    assert pedido.codigo in client.get(reverse("pedidos:meus_pedidos")).content.decode()
    r = client.post(reverse("pedidos:cancelar", args=[pedido.pk]), follow=True)
    assert "cancelado" in r.content.decode()
    produto.refresh_from_db()
    assert produto.estoque == 10


def test_us07_us12_us15_admin_gerencia_loja(client, admin, cliente, categoria, endereco):
    """
    Dado que sou administrador
    Quando cadastro um cupcake, um cliente o compra e eu despacho o pedido
    Então o cupcake aparece na vitrine e o painel mostra a venda do dia
    """
    client.force_login(admin)
    client.post(reverse("painel:novo", args=["produtos"]), {
        "nome": "Doce de Leite", "categoria": categoria.pk, "descricao": "Cremoso", "preco": "12.00",
        "estoque": 10, "imagem": "img/cupcakes/caramelo.svg", "ativo": "on",
    })
    assert "Doce de Leite" in client.get(reverse("catalogo:vitrine")).content.decode()

    from catalogo.models import Produto
    p = Produto.objects.get(nome="Doce de Leite")
    client.force_login(cliente)
    client.post(reverse("pedidos:carrinho_adicionar", args=[p.pk]), {"quantidade": 3})
    client.post(reverse("pedidos:checkout"), {"tipo_entrega": "ENTREGA", "endereco": endereco.pk, "metodo_pagamento": "NA_ENTREGA"})

    client.force_login(admin)
    r = client.get(reverse("painel:inicio"))
    assert r.context["resumo"].pedidos == 1
    assert "R$ 41,00" in r.content.decode()  # 3 x 12,00 + 5,00

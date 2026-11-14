"""Testes de integração: controllers + templates + banco via cliente HTTP."""
from decimal import Decimal

import pytest
from django.urls import reverse

from catalogo.models import Categoria, Produto
from contas.models import Usuario
from pedidos.models import Pedido, ZonaEntrega

pytestmark = pytest.mark.integracao


# ---------------- vitrine ----------------
def test_vitrine_mostra_apenas_disponiveis(client, produto, categoria):
    Produto.objects.create(categoria=categoria, nome="Inativo", descricao="x", preco=1, estoque=5, ativo=False)
    Produto.objects.create(categoria=categoria, nome="Esgotado", descricao="x", preco=1, estoque=0)
    html = client.get(reverse("catalogo:vitrine")).content.decode()
    assert "Morango" in html
    assert "Inativo" not in html and "Esgotado" not in html


def test_vitrine_filtra_por_categoria_e_busca(client, produto):
    outra = Categoria.objects.create(nome="Veganos")
    Produto.objects.create(categoria=outra, nome="Limão Vegano", descricao="cítrico", preco=1, estoque=5)
    r = client.get(reverse("catalogo:vitrine"), {"categoria": "veganos"})
    assert "Limão Vegano" in r.content.decode() and "Morango" not in r.content.decode()
    r = client.get(reverse("catalogo:vitrine"), {"q": "cítrico"})
    assert list(r.context["produtos"]) == [Produto.objects.get(nome="Limão Vegano")]


def test_busca_sem_resultado_mostra_mensagem(client, produto):
    r = client.get(reverse("catalogo:vitrine"), {"q": "jiló"})
    assert "Nenhum cupcake encontrado" in r.content.decode()


def test_detalhe_de_produto_inativo_da_404(client, produto):
    produto.ativo = False
    produto.save()
    assert client.get(reverse("catalogo:detalhe", args=[produto.pk])).status_code == 404


def test_pagina_404_amigavel(client, db):
    r = client.get("/nao-existe/")
    assert r.status_code == 404


# ---------------- contas ----------------
def test_cadastro_cria_cliente_e_loga(client, db):
    r = client.post(reverse("contas:cadastro"), {
        "nome": "Carla", "email": "Carla@Teste.com", "telefone": "", "senha": "Cupcake#2026",
        "confirmacao": "Cupcake#2026", "aceite": "on",
    })
    assert r.status_code == 302
    u = Usuario.objects.get(email="carla@teste.com")
    assert u.perfil == Usuario.Perfil.CLIENTE and u.check_password("Cupcake#2026")
    assert client.get(reverse("contas:perfil")).status_code == 200


def test_cadastro_valida_senha_email_e_lgpd(client, cliente):
    r = client.post(reverse("contas:cadastro"), {
        "nome": "X", "email": "ana@teste.com", "senha": "123", "confirmacao": "321",
    })
    erros = r.context["form"].errors
    assert {"email", "senha", "confirmacao", "aceite"} <= set(erros)


def test_login_com_erro_mostra_mensagem(client, cliente):
    r = client.post(reverse("contas:entrar"), {"username": "ana@teste.com", "password": "errada"})
    assert "E-mail ou senha incorretos" in r.content.decode()


def test_login_admin_vai_para_painel(client, admin):
    r = client.post(reverse("contas:entrar"), {"username": "admin@teste.com", "password": "SenhaForte@1"})
    assert r.url == "/painel/"


def test_open_redirect_bloqueado(client, db):
    r = client.post(reverse("contas:cadastro") + "?next=https://malicioso.com", {
        "nome": "D", "email": "d@t.com", "senha": "Cupcake#2026", "confirmacao": "Cupcake#2026", "aceite": "on",
    })
    assert r.url == "/"


def test_endereco_principal_unico(cliente_http, cliente, endereco):
    cliente_http.post(reverse("contas:endereco_novo"), {
        "apelido": "Trabalho", "cep": "01001-000", "logradouro": "Av B", "numero": "2",
        "bairro": "Centro", "cidade": "SP", "principal": "on",
    })
    assert list(cliente.enderecos.filter(principal=True).values_list("apelido", flat=True)) == ["Trabalho"]


def test_nao_edita_endereco_de_outro(client, outro_cliente, endereco):
    client.force_login(outro_cliente)
    assert client.get(reverse("contas:endereco_editar", args=[endereco.pk])).status_code == 404


def test_logout_exige_post(cliente_http):
    assert cliente_http.get(reverse("contas:sair")).status_code == 405


# ---------------- carrinho e checkout ----------------
def test_adicionar_ao_carrinho_e_badge(client, produto):
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 2})
    r = client.get(reverse("pedidos:carrinho"))
    assert r.context["carrinho_qtd"] == 2
    assert "R$ 20,00" in r.content.decode()


def test_adicionar_acima_do_estoque_mostra_erro(client, produto):
    r = client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 11}, follow=True)
    assert "Só temos 10" in r.content.decode()
    r = client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 99}, follow=True)
    assert "Máximo de 50" in r.content.decode()


def test_quantidade_nao_numerica(client, produto):
    r = client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": "abc"}, follow=True)
    assert "pelo menos 1" in r.content.decode()


def test_checkout_exige_login(client, produto):
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]))
    r = client.get(reverse("pedidos:checkout"))
    assert r.status_code == 302 and "/conta/entrar/" in r.url


def test_checkout_com_carrinho_vazio_volta_para_vitrine(cliente_http):
    assert cliente_http.get(reverse("pedidos:checkout")).url == "/"


def test_checkout_mostra_taxa_e_bairro_nao_atendido(cliente_http, produto, endereco, endereco_fora):
    cliente_http.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]))
    html = cliente_http.get(reverse("pedidos:checkout")).content.decode()
    assert "Taxa: R$ 5,00" in html
    assert "Ainda não entregamos neste bairro" in html


def test_checkout_pix_redireciona_para_pagamento(cliente_http, produto, endereco):
    cliente_http.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 3})
    r = cliente_http.post(reverse("pedidos:checkout"), {
        "tipo_entrega": "ENTREGA", "endereco": endereco.pk, "metodo_pagamento": "PIX",
    })
    pedido = Pedido.objects.get()
    assert r.url == reverse("pedidos:pagamento", args=[pedido.pk])
    assert pedido.total == Decimal("35.00")
    assert "PIXSIMULADO" in cliente_http.get(r.url).content.decode()


def test_checkout_endereco_de_outro_usuario_e_ignorado(client, outro_cliente, produto, endereco):
    client.force_login(outro_cliente)
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]))
    r = client.post(reverse("pedidos:checkout"), {"tipo_entrega": "ENTREGA", "endereco": endereco.pk, "metodo_pagamento": "PIX"})
    assert "Escolha um endereço" in r.content.decode()
    assert not Pedido.objects.exists()


def test_pagina_de_pagamento_e_pagar(cliente_http, produto, endereco):
    cliente_http.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]))
    cliente_http.post(reverse("pedidos:checkout"), {"tipo_entrega": "RETIRADA", "metodo_pagamento": "CARTAO"})
    pedido = Pedido.objects.get()
    r = cliente_http.post(reverse("pedidos:pagamento", args=[pedido.pk]), follow=True)
    assert "Pagamento aprovado" in r.content.decode()
    # pedido pago: página de pagamento redireciona para o detalhe
    assert cliente_http.get(reverse("pedidos:pagamento", args=[pedido.pk])).status_code == 302


def test_pagamento_recusado_mostra_erro_e_permite_nova_tentativa(cliente_http, produto):
    cliente_http.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]))
    cliente_http.post(reverse("pedidos:checkout"), {"tipo_entrega": "RETIRADA", "metodo_pagamento": "CARTAO"})
    url = reverse("pedidos:pagamento", args=[Pedido.objects.get().pk])
    r = cliente_http.post(url, {"simular": "recusa"}, follow=True)
    html = r.content.decode()
    assert "recusado pela operadora" in html and "A última tentativa foi recusada" in html
    r = cliente_http.post(url, follow=True)
    assert "Pagamento aprovado" in r.content.decode()


# ---------------- autorização (RN07) ----------------
def test_cliente_nao_ve_pedido_de_outro(client, cliente, outro_cliente, produto, endereco):
    pedido = Pedido.objects.create(usuario=cliente, tipo_entrega="RETIRADA")
    client.force_login(outro_cliente)
    assert client.get(reverse("pedidos:detalhe", args=[pedido.pk])).status_code == 404
    assert client.post(reverse("pedidos:cancelar", args=[pedido.pk])).status_code == 404


@pytest.mark.parametrize("nome,args", [("painel:inicio", []), ("painel:lista", ["produtos"]), ("painel:novo", ["zonas"])])
def test_painel_bloqueado_para_cliente(cliente_http, nome, args):
    assert cliente_http.get(reverse(nome, args=args)).status_code == 403


def test_painel_redireciona_anonimo_para_login(client, db):
    assert "/conta/entrar/" in client.get(reverse("painel:inicio")).url


def test_csrf_ativo(client, produto):
    from django.test import Client

    c = Client(enforce_csrf_checks=True)
    assert c.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk])).status_code == 403


# ---------------- painel ----------------
def test_painel_crud_produto(admin_http, categoria):
    r = admin_http.post(reverse("painel:novo", args=["produtos"]), {
        "nome": "Novo Sabor", "categoria": categoria.pk, "descricao": "desc", "preco": "15.50",
        "estoque": 20, "imagem": "img/cupcakes/limao.svg", "ativo": "on",
    })
    assert r.status_code == 302
    p = Produto.objects.get(nome="Novo Sabor")
    admin_http.post(reverse("painel:editar", args=["produtos", p.pk]), {
        "nome": "Novo Sabor", "categoria": categoria.pk, "descricao": "desc", "preco": "16.00",
        "estoque": 20, "imagem": "img/cupcakes/limao.svg",
    })
    p.refresh_from_db()
    assert p.preco == Decimal("16.00") and p.ativo is False


def test_painel_valida_preco(admin_http, categoria):
    r = admin_http.post(reverse("painel:novo", args=["produtos"]), {
        "nome": "X", "categoria": categoria.pk, "descricao": "d", "preco": "0", "estoque": 1, "imagem": "img/cupcakes/limao.svg",
    })
    assert "preco" in r.context["form"].errors


def test_excluir_produto_com_pedido_apenas_desativa(admin_http, cliente, produto):
    pedido = Pedido.objects.create(usuario=cliente, tipo_entrega="RETIRADA")
    pedido.itens.create(produto=produto, nome_produto="Morango", quantidade=1, preco_unitario=10)
    r = admin_http.post(reverse("painel:excluir", args=["produtos", produto.pk]), follow=True)
    produto.refresh_from_db()
    assert produto.ativo is False
    assert "desativado" in r.content.decode()


def test_excluir_zona_sem_vinculo(admin_http, zona):
    admin_http.post(reverse("painel:excluir", args=["zonas", zona.pk]))
    assert not ZonaEntrega.objects.exists()


def test_tipo_de_cadastro_invalido_404(admin_http):
    assert admin_http.get("/painel/usuarios/").status_code == 404


def test_painel_avanca_pedido_e_mostra_erro_de_regra(admin_http, cliente, carrinho, produto, endereco):
    from pedidos import services

    carrinho.adicionar(produto)
    pedido = services.criar_pedido(cliente, carrinho, "ENTREGA", "PIX", endereco)
    r = admin_http.post(reverse("painel:pedido_avancar", args=[pedido.pk]), follow=True)
    assert "Aguardando confirmação do pagamento" in r.content.decode()
    services.pagar_pedido(pedido)
    admin_http.post(reverse("painel:pedido_avancar", args=[pedido.pk]))
    pedido.refresh_from_db()
    assert pedido.status == Pedido.Status.EM_PREPARO
    html = admin_http.get(reverse("painel:inicio")).content.decode()
    assert pedido.codigo in html and "Saiu para entrega" in html


def test_painel_detalhe_e_cancelamento(admin_http, cliente, carrinho, produto, endereco):
    from pedidos import services

    carrinho.adicionar(produto, 2)
    pedido = services.criar_pedido(cliente, carrinho, "ENTREGA", "NA_ENTREGA", endereco)
    assert admin_http.get(reverse("painel:pedido_detalhe", args=[pedido.pk])).status_code == 200
    admin_http.post(reverse("painel:pedido_cancelar", args=[pedido.pk]))
    produto.refresh_from_db()
    assert produto.estoque == 10


def test_paginas_publicas_respondem(client, zona):
    for url in ["/", "/sobre/", "/entregas/", "/carrinho/", "/conta/entrar/", "/conta/cadastro/", "/manifest.webmanifest", "/sw.js"]:
        assert client.get(url).status_code == 200, url

"""Regressão dos apontamentos dos testadores externos (laudo de qualidade, B02–B06)."""
from decimal import Decimal

import pytest
from django.urls import reverse

from catalogo.models import Categoria, Produto
from catalogo.texto import normalizar
from contas.models import Endereco
from pedidos import services
from pedidos.models import ZonaEntrega


# ---------------- B06: busca e bairro sem acentos ----------------
@pytest.mark.unitario
@pytest.mark.parametrize("entrada,esperado", [
    ("Verão", "verao"), ("VERAO", "verao"), ("  Pão   de  Açúcar ", "pao de acucar"),
    ("São Paulo", "sao paulo"), ("", ""), (None, ""),
])
def test_normalizar(entrada, esperado):
    assert normalizar(entrada) == esperado


@pytest.fixture
def blueberry(db):
    cat = Categoria.objects.create(nome="Sazonais")
    return Produto.objects.create(categoria=cat, nome="Blueberry de Verão", descricao="Mirtilos frescos",
                                  ingredientes="iogurte, açúcar", preco=Decimal("12.90"), estoque=5)


@pytest.mark.integracao
@pytest.mark.parametrize("termo", ["Verao", "verão", "VERÃO", "acucar", "sazonais", "mirtilo"])
def test_b06_busca_ignora_acentos_e_maiusculas(client, blueberry, termo):
    r = client.get(reverse("catalogo:vitrine"), {"q": termo})
    assert list(r.context["produtos"]) == [blueberry]


@pytest.mark.integracao
def test_b06_texto_de_busca_acompanha_edicoes(blueberry):
    blueberry.nome = "Framboesa de Inverno"
    blueberry.save()
    assert "framboesa de inverno" in blueberry.texto_busca and "verao" not in blueberry.texto_busca
    blueberry.categoria.nome = "Edição Limitada"
    blueberry.categoria.save()
    blueberry.refresh_from_db()
    assert "edicao limitada" in blueberry.texto_busca


@pytest.mark.unitario
def test_b06_bairro_sem_acento_encontra_zona(db):
    ZonaEntrega.objects.create(bairro="São Mateus", taxa=Decimal("6.00"))
    assert services.calcular_taxa("ENTREGA", "sao  mateus") == Decimal("6.00")
    assert services.calcular_taxa("ENTREGA", "SÃO MATEUS") == Decimal("6.00")


@pytest.mark.integracao
def test_b06_checkout_reconhece_bairro_sem_acento(cliente_http, cliente, produto):
    ZonaEntrega.objects.create(bairro="Moóca", taxa=Decimal("10.00"))
    Endereco.objects.create(usuario=cliente, logradouro="Rua X", numero="1", bairro="mooca", cep="03100-000")
    cliente_http.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]))
    html = cliente_http.get(reverse("pedidos:checkout")).content.decode()
    assert "Taxa: R$ 10,00" in html and "Ainda não entregamos" not in html


# ---------------- B02: alterar senha ----------------
@pytest.mark.integracao
def test_b02_alterar_senha(cliente_http, cliente):
    assert "Alterar senha" in cliente_http.get(reverse("contas:perfil")).content.decode()
    r = cliente_http.post(reverse("contas:alterar_senha"), {
        "old_password": "SenhaForte@1", "new_password1": "Cupcake#Nova9", "new_password2": "Cupcake#Nova9",
    }, follow=True)
    assert "Senha alterada com sucesso" in r.content.decode()
    cliente.refresh_from_db()
    assert cliente.check_password("Cupcake#Nova9")
    assert cliente_http.get(reverse("contas:perfil")).status_code == 200  # continua logado


@pytest.mark.integracao
def test_b02_alterar_senha_valida_senha_atual(cliente_http, cliente):
    r = cliente_http.post(reverse("contas:alterar_senha"), {
        "old_password": "errada", "new_password1": "Cupcake#Nova9", "new_password2": "Cupcake#Nova9",
    })
    assert r.status_code == 200 and "old_password" in r.context["form"].errors
    cliente.refresh_from_db()
    assert cliente.check_password("SenhaForte@1")


@pytest.mark.integracao
def test_b02_alterar_senha_exige_login(client, db):
    assert "/conta/entrar/" in client.get(reverse("contas:alterar_senha")).url


# ---------------- B03: contador de unidades ----------------
@pytest.mark.integracao
def test_b03_carrinho_mostra_total_de_unidades(client, produto, produto2):
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto.pk]), {"quantidade": 2})
    client.post(reverse("pedidos:carrinho_adicionar", args=[produto2.pk]), {"quantidade": 1})
    html = client.get(reverse("pedidos:carrinho")).content.decode()
    assert "(3 unidades)" in html and "3 unidades" in html


# ---------------- B04/B05: espaçamento ----------------
@pytest.mark.unitario
def test_b04_padding_do_main_vence_o_container():
    from pathlib import Path

    css = (Path(__file__).resolve().parent.parent / "static/css/app.css").read_text(encoding="utf-8")
    assert "main.container { padding-top: 24px" in css

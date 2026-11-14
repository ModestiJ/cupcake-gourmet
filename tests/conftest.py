from decimal import Decimal

import pytest
from django.contrib.sessions.backends.signed_cookies import SessionStore

from catalogo.models import Categoria, Produto
from contas.models import Endereco, Usuario
from pedidos.carrinho import Carrinho
from pedidos.models import ZonaEntrega


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome="Clássicos")


@pytest.fixture
def produto(categoria):
    return Produto.objects.create(categoria=categoria, nome="Morango", descricao="d", preco=Decimal("10.00"), estoque=10)


@pytest.fixture
def produto2(categoria):
    return Produto.objects.create(categoria=categoria, nome="Chocolate", descricao="d", preco=Decimal("12.50"), estoque=5)


@pytest.fixture
def zona(db):
    return ZonaEntrega.objects.create(bairro="Centro", taxa=Decimal("5.00"))


@pytest.fixture
def cliente(db):
    return Usuario.objects.create_user(email="ana@teste.com", password="SenhaForte@1", nome="Ana Cliente")


@pytest.fixture
def outro_cliente(db):
    return Usuario.objects.create_user(email="bia@teste.com", password="SenhaForte@1", nome="Bia Cliente")


@pytest.fixture
def admin(db):
    return Usuario.objects.create_superuser(email="admin@teste.com", password="SenhaForte@1", nome="Admin")


@pytest.fixture
def endereco(cliente, zona):
    return Endereco.objects.create(usuario=cliente, logradouro="Rua A", numero="1", bairro="Centro", cep="01000-000", principal=True)


@pytest.fixture
def endereco_fora(cliente):
    return Endereco.objects.create(usuario=cliente, apelido="Sítio", logradouro="Estrada B", numero="2", bairro="Longe", cep="09000-000")


@pytest.fixture
def carrinho():
    return Carrinho(SessionStore())


@pytest.fixture
def cliente_http(client, cliente):
    client.force_login(cliente)
    return client


@pytest.fixture
def admin_http(client, admin):
    client.force_login(admin)
    return client

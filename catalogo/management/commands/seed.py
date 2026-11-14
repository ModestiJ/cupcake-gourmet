"""Popula o banco com dados de demonstração. Idempotente: pode rodar a cada deploy.

Uso: python manage.py seed [--repor-estoque]
Admin: variáveis ADMIN_EMAIL e ADMIN_PASSWORD (obrigatórias quando DEBUG=0).
"""
import os
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalogo.models import Categoria, Produto
from contas.models import Endereco, Usuario
from pedidos.models import ZonaEntrega

CATEGORIAS = [("Clássicos", 1), ("Gourmet", 2), ("Veganos", 3), ("Sazonais", 4)]

PRODUTOS = [
    # nome, categoria, preço, imagem, destaque, descrição, ingredientes
    ("Morango com Chantilly", "Clássicos", "9.90", "morango", True,
     "Massa de baunilha, recheio de geleia de morango e chantilly batido na hora.", "farinha, ovos, manteiga, morango, creme de leite"),
    ("Chocolate Belga", "Clássicos", "10.90", "chocolate", True,
     "Massa de cacau 70% com ganache de chocolate belga e raspas crocantes.", "farinha, cacau, chocolate belga, ovos, manteiga"),
    ("Baunilha de Madagascar", "Clássicos", "8.90", "baunilha", False,
     "O clássico perfeito: baunilha em fava e buttercream suave.", "farinha, fava de baunilha, ovos, manteiga, açúcar"),
    ("Pistache Siciliano", "Gourmet", "14.90", "pistache", True,
     "Massa amanteigada com creme de pistache siciliano e pistache torrado.", "farinha, pistache, ovos, manteiga, chocolate branco"),
    ("Red Velvet", "Gourmet", "12.90", "red-velvet", False,
     "Massa aveludada de cacau e cobertura de cream cheese.", "farinha, cacau, buttermilk, cream cheese, manteiga"),
    ("Caramelo Salgado", "Gourmet", "13.90", "caramelo", True,
     "Recheio de caramelo com flor de sal e cobertura de doce de leite.", "farinha, açúcar mascavo, flor de sal, creme de leite"),
    ("Limão Siciliano Vegano", "Veganos", "11.90", "limao", False,
     "Massa vegana cítrica com cobertura de creme de coco e raspas de limão.", "farinha, leite vegetal, óleo de coco, limão siciliano"),
    ("Chocolate Vegano", "Veganos", "11.90", "chocolate", False,
     "Cacau intenso sem ingredientes de origem animal.", "farinha, cacau, leite de aveia, óleo vegetal"),
    ("Blueberry de Verão", "Sazonais", "12.90", "blueberry", False,
     "Edição limitada com mirtilos frescos e cobertura de iogurte.", "farinha, mirtilo, iogurte, ovos, manteiga"),
]

ZONAS = [("Centro", "5.00"), ("Jardins", "7.00"), ("Vila Mariana", "8.00"), ("Pinheiros", "8.00"),
         ("Moema", "9.00"), ("Mooca", "10.00"), ("Santana", "12.00")]


class Command(BaseCommand):
    help = "Cria dados de demonstração (categorias, cupcakes, zonas, admin e cliente demo)."

    def add_arguments(self, parser):
        parser.add_argument("--repor-estoque", action="store_true", help="Volta o estoque de todos os produtos para 40.")

    @transaction.atomic
    def handle(self, *args, **opts):
        cats = {}
        for nome, ordem in CATEGORIAS:
            cats[nome], _ = Categoria.objects.get_or_create(nome=nome, defaults={"ordem": ordem})

        for nome, cat, preco, img, destaque, desc, ingr in PRODUTOS:
            p, criado = Produto.objects.get_or_create(
                categoria=cats[cat], nome=nome,
                defaults=dict(preco=Decimal(preco), imagem=f"img/cupcakes/{img}.svg", destaque=destaque,
                              descricao=desc, ingredientes=ingr, estoque=40),
            )
            if opts["repor_estoque"] and not criado:
                p.estoque = 40
                p.save(update_fields=["estoque"])

        for bairro, taxa in ZONAS:
            ZonaEntrega.objects.get_or_create(bairro=bairro, defaults={"taxa": Decimal(taxa)})

        email = os.environ.get("ADMIN_EMAIL") or ("admin@cupcake.dev" if settings.DEBUG else None)
        senha = os.environ.get("ADMIN_PASSWORD") or ("Admin@12345" if settings.DEBUG else None)
        if not email or not senha:
            raise CommandError("Defina ADMIN_EMAIL e ADMIN_PASSWORD em produção.")
        if not Usuario.objects.filter(email=email).exists():
            Usuario.objects.create_superuser(email=email, password=senha, nome="Administrador da Loja")

        demo_senha = os.environ.get("DEMO_PASSWORD", "Cliente@123")
        cliente, criado = Usuario.objects.get_or_create(email="cliente@cupcake.dev", defaults={"nome": "Cliente Demonstração"})
        if criado:
            cliente.set_password(demo_senha)
            cliente.save()
            Endereco.objects.create(usuario=cliente, apelido="Casa", logradouro="Rua das Flores", numero="123",
                                    bairro="Vila Mariana", cidade="São Paulo", cep="04101-000", principal=True)

        self.stdout.write(self.style.SUCCESS(
            f"Seed ok: {Categoria.objects.count()} categorias, {Produto.objects.count()} cupcakes, "
            f"{ZonaEntrega.objects.count()} zonas. Admin: {email}"
        ))

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

ILUSTRACOES = [
    ("img/cupcakes/morango.svg", "Morango"),
    ("img/cupcakes/chocolate.svg", "Chocolate"),
    ("img/cupcakes/baunilha.svg", "Baunilha"),
    ("img/cupcakes/pistache.svg", "Pistache"),
    ("img/cupcakes/red-velvet.svg", "Red velvet"),
    ("img/cupcakes/limao.svg", "Limão"),
    ("img/cupcakes/blueberry.svg", "Blueberry"),
    ("img/cupcakes/caramelo.svg", "Caramelo"),
]


class Categoria(models.Model):
    """Agrupador da vitrine (US04, US08)."""

    nome = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    ativa = models.BooleanField(default=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "categoria"
        ordering = ["ordem", "nome"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class ProdutoQuerySet(models.QuerySet):
    def disponiveis(self):
        """RN01: só aparece na vitrine produto ativo, com estoque e de categoria ativa."""
        return self.filter(ativo=True, estoque__gt=0, categoria__ativa=True)


class Produto(models.Model):
    """Cupcake vendido na loja (US05, US07)."""

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="produtos")
    nome = models.CharField(max_length=80)
    descricao = models.TextField("descrição", max_length=600)
    ingredientes = models.CharField(max_length=300, blank=True)
    preco = models.DecimalField(
        "preço", max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    estoque = models.PositiveIntegerField(default=0, help_text="Unidades disponíveis hoje.")
    imagem = models.CharField(max_length=120, choices=ILUSTRACOES, default=ILUSTRACOES[0][0])
    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ProdutoQuerySet.as_manager()

    class Meta:
        db_table = "produto"
        ordering = ["-destaque", "nome"]
        constraints = [
            models.CheckConstraint(condition=models.Q(preco__gt=0), name="ck_produto_preco_positivo"),
            models.CheckConstraint(condition=models.Q(estoque__gte=0), name="ck_produto_estoque_nao_negativo"),
            models.UniqueConstraint(fields=["categoria", "nome"], name="uq_produto_categoria_nome"),
        ]

    @property
    def disponivel(self) -> bool:
        return self.ativo and self.estoque > 0 and self.categoria.ativa

    def __str__(self):
        return self.nome

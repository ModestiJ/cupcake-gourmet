from decimal import Decimal

from django.conf import settings
from django.db import models


class ZonaEntrega(models.Model):
    """Bairro atendido e sua taxa de entrega (US16, RN05)."""

    bairro = models.CharField(max_length=80, unique=True)
    taxa = models.DecimalField(max_digits=6, decimal_places=2)
    ativa = models.BooleanField(default=True)

    class Meta:
        db_table = "zona_entrega"
        verbose_name = "zona de entrega"
        verbose_name_plural = "zonas de entrega"
        ordering = ["bairro"]
        constraints = [models.CheckConstraint(condition=models.Q(taxa__gte=0), name="ck_zona_taxa_nao_negativa")]

    def __str__(self):
        return f"{self.bairro} (R$ {self.taxa})"


class Pedido(models.Model):
    """Pedido do cliente (US10, US11, US12)."""

    class Tipo(models.TextChoices):
        ENTREGA = "ENTREGA", "Entrega"
        RETIRADA = "RETIRADA", "Retirada na loja"

    class Status(models.TextChoices):
        RECEBIDO = "RECEBIDO", "Recebido"
        EM_PREPARO = "EM_PREPARO", "Em preparo"
        SAIU_PARA_ENTREGA = "SAIU_PARA_ENTREGA", "Saiu para entrega"
        PRONTO_RETIRADA = "PRONTO_RETIRADA", "Pronto para retirada"
        ENTREGUE = "ENTREGUE", "Entregue"
        CANCELADO = "CANCELADO", "Cancelado"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos")
    tipo_entrega = models.CharField(max_length=10, choices=Tipo.choices)
    endereco_entrega = models.CharField(
        max_length=300, blank=True, help_text="Cópia do endereço no momento do pedido."
    )
    bairro = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEBIDO)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    taxa_entrega = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    observacao = models.CharField(max_length=300, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pedido"
        ordering = ["-criado_em"]
        constraints = [
            models.CheckConstraint(condition=models.Q(total__gte=0), name="ck_pedido_total_nao_negativo"),
            models.CheckConstraint(
                condition=models.Q(tipo_entrega="RETIRADA", taxa_entrega=0) | models.Q(tipo_entrega="ENTREGA"),
                name="ck_pedido_retirada_sem_taxa",
            ),
        ]

    @property
    def codigo(self) -> str:
        return f"#{self.pk:05d}"

    @property
    def finalizado(self) -> bool:
        return self.status in {self.Status.ENTREGUE, self.Status.CANCELADO}

    def __str__(self):
        return f"Pedido {self.codigo}"


class ItemPedido(models.Model):
    """Linha do pedido. O preço é congelado no momento da compra (RN02)."""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey("catalogo.Produto", on_delete=models.PROTECT, related_name="itens_pedido")
    nome_produto = models.CharField(max_length=80)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        db_table = "item_pedido"
        verbose_name = "item do pedido"
        constraints = [
            models.CheckConstraint(condition=models.Q(quantidade__gt=0), name="ck_item_quantidade_positiva"),
            models.UniqueConstraint(fields=["pedido", "produto"], name="uq_item_pedido_produto"),
        ]

    @property
    def total(self) -> Decimal:
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.nome_produto}"


class Pagamento(models.Model):
    """Pagamento do pedido, 1:1 (US13, US14)."""

    class Metodo(models.TextChoices):
        PIX = "PIX", "Pix"
        CARTAO = "CARTAO", "Cartão (online)"
        NA_ENTREGA = "NA_ENTREGA", "Pagar na entrega/retirada"

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        APROVADO = "APROVADO", "Aprovado"
        RECUSADO = "RECUSADO", "Recusado"
        ESTORNADO = "ESTORNADO", "Estornado"

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="pagamento")
    metodo = models.CharField(max_length=12, choices=Metodo.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    transacao_ref = models.CharField(max_length=64, blank=True)
    pago_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "pagamento"

    @property
    def liberado_para_preparo(self) -> bool:
        """RN08: só vai para preparo se pago online ou se o pagamento é na entrega."""
        return self.status == self.Status.APROVADO or self.metodo == self.Metodo.NA_ENTREGA

    def __str__(self):
        return f"{self.get_metodo_display()} – {self.get_status_display()}"


class HistoricoStatus(models.Model):
    """Trilha de mudanças de status; alimenta a linha do tempo (US17)."""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="historico")
    status = models.CharField(max_length=20, choices=Pedido.Status.choices)
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    alterado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "historico_status"
        verbose_name = "histórico de status"
        ordering = ["alterado_em", "id"]

    def __str__(self):
        return f"{self.pedido} → {self.status}"

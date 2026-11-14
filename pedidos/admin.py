from django.contrib import admin

from .models import HistoricoStatus, ItemPedido, Pagamento, Pedido, ZonaEntrega


class ItemInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ["produto", "nome_produto", "quantidade", "preco_unitario"]


class HistoricoInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0
    readonly_fields = ["status", "alterado_por", "alterado_em"]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "usuario", "tipo_entrega", "status", "total", "criado_em"]
    list_filter = ["status", "tipo_entrega"]
    inlines = [ItemInline, HistoricoInline]


admin.site.register(ZonaEntrega)
admin.site.register(Pagamento)

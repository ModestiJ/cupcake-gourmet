from django.contrib import admin

from .models import Categoria, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "ordem", "ativa"]
    prepopulated_fields = {"slug": ["nome"]}


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ["nome", "categoria", "preco", "estoque", "ativo", "destaque"]
    list_filter = ["categoria", "ativo", "destaque"]
    search_fields = ["nome", "descricao"]

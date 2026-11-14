from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Endereco, Usuario


class EnderecoInline(admin.TabularInline):
    model = Endereco
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ["email"]
    list_display = ["email", "nome", "perfil", "is_active", "criado_em"]
    list_filter = ["perfil", "is_active"]
    search_fields = ["email", "nome"]
    inlines = [EnderecoInline]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Dados", {"fields": ["nome", "telefone", "perfil"]}),
        ("Permissões", {"fields": ["is_active", "is_staff", "is_superuser"]}),
    ]
    add_fieldsets = [(None, {"classes": ["wide"], "fields": ["email", "nome", "perfil", "password1", "password2"]})]

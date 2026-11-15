from django.urls import path

from . import views

app_name = "contas"

urlpatterns = [
    path("cadastro/", views.cadastrar, name="cadastro"),
    path("entrar/", views.EntrarView.as_view(), name="entrar"),
    path("sair/", views.SairView.as_view(), name="sair"),
    path("perfil/", views.perfil, name="perfil"),
    path("senha/", views.AlterarSenhaView.as_view(), name="alterar_senha"),
    path("enderecos/novo/", views.endereco_form, name="endereco_novo"),
    path("enderecos/<int:pk>/editar/", views.endereco_form, name="endereco_editar"),
    path("enderecos/<int:pk>/excluir/", views.endereco_excluir, name="endereco_excluir"),
]

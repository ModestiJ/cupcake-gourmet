from django.urls import path

from . import views

app_name = "painel"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("pedidos/<int:pk>/", views.pedido_detalhe, name="pedido_detalhe"),
    path("pedidos/<int:pk>/avancar/", views.pedido_avancar, name="pedido_avancar"),
    path("pedidos/<int:pk>/cancelar/", views.pedido_cancelar, name="pedido_cancelar"),
    path("<str:tipo>/", views.lista, name="lista"),
    path("<str:tipo>/novo/", views.formulario, name="novo"),
    path("<str:tipo>/<int:pk>/", views.formulario, name="editar"),
    path("<str:tipo>/<int:pk>/excluir/", views.excluir, name="excluir"),
]

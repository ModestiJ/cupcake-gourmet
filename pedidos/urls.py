from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("carrinho/", views.carrinho_ver, name="carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", views.carrinho_adicionar, name="carrinho_adicionar"),
    path("carrinho/atualizar/<int:produto_id>/", views.carrinho_atualizar, name="carrinho_atualizar"),
    path("carrinho/remover/<int:produto_id>/", views.carrinho_remover, name="carrinho_remover"),
    path("checkout/", views.checkout, name="checkout"),
    path("pedidos/", views.meus_pedidos, name="meus_pedidos"),
    path("pedidos/<int:pk>/", views.detalhe, name="detalhe"),
    path("pedidos/<int:pk>/pagamento/", views.pagamento, name="pagamento"),
    path("pedidos/<int:pk>/cancelar/", views.cancelar, name="cancelar"),
    path("entregas/", views.areas_entrega, name="areas_entrega"),
]

from django.urls import path

from . import views

app_name = "catalogo"

urlpatterns = [
    path("", views.vitrine, name="vitrine"),
    path("cupcake/<int:pk>/", views.detalhe, name="detalhe"),
    path("sobre/", views.sobre, name="sobre"),
]

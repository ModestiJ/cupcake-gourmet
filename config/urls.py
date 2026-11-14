from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("conta/", include("contas.urls")),
    path("painel/", include("painel.urls")),
    path("", include("pedidos.urls")),
    path("", include("catalogo.urls")),
    path("manifest.webmanifest", TemplateView.as_view(template_name="pwa/manifest.webmanifest", content_type="application/manifest+json")),
    path("sw.js", TemplateView.as_view(template_name="pwa/sw.js", content_type="application/javascript")),
]

handler404 = "config.views.nao_encontrado"
handler403 = "config.views.proibido"
handler500 = "config.views.erro_servidor"

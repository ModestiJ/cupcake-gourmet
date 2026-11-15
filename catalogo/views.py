from django.shortcuts import get_object_or_404, render

from .models import Categoria, Produto
from .texto import normalizar


def vitrine(request):
    """US04 (por categoria) e US06 (busca)."""
    produtos = Produto.objects.disponiveis().select_related("categoria")
    categorias = Categoria.objects.filter(ativa=True, produtos__ativo=True, produtos__estoque__gt=0).distinct()

    slug = request.GET.get("categoria", "")
    categoria_atual = None
    if slug:
        categoria_atual = categorias.filter(slug=slug).first()
        produtos = produtos.filter(categoria=categoria_atual) if categoria_atual else produtos.none()

    termo = request.GET.get("q", "").strip()[:60]
    if termo:
        # B06: busca sem acentos e sem diferenciar maiúsculas ("Verao" acha "Verão").
        produtos = produtos.filter(texto_busca__contains=normalizar(termo))

    destaques = Produto.objects.disponiveis().filter(destaque=True)[:4] if not (slug or termo) else []
    return render(
        request,
        "catalogo/vitrine.html",
        {
            "produtos": produtos,
            "categorias": categorias,
            "categoria_atual": categoria_atual,
            "termo": termo,
            "destaques": destaques,
        },
    )


def detalhe(request, pk):
    """US05 – detalhes do cupcake. Produto inativo responde 404 (RN01)."""
    produto = get_object_or_404(Produto.objects.select_related("categoria"), pk=pk, ativo=True, categoria__ativa=True)
    relacionados = Produto.objects.disponiveis().filter(categoria=produto.categoria).exclude(pk=pk)[:3]
    return render(request, "catalogo/detalhe.html", {"produto": produto, "relacionados": relacionados})


def sobre(request):
    return render(request, "catalogo/sobre.html")

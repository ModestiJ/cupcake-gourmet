from .carrinho import CHAVE_SESSAO


def carrinho(request):
    """Quantidade de itens no carrinho para o badge do cabeçalho."""
    itens = request.session.get(CHAVE_SESSAO, {}) if hasattr(request, "session") else {}
    return {"carrinho_qtd": sum(itens.values())}

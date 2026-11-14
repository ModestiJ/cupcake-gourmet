"""Páginas de erro amigáveis (RNF04 – mensagens claras)."""
from django.shortcuts import render


def nao_encontrado(request, exception=None):
    return render(request, "erro.html", {"codigo": 404, "titulo": "Página não encontrada",
                                         "mensagem": "Esse cupcake saiu do forno e sumiu. Confira o endereço ou volte à vitrine."}, status=404)


def proibido(request, exception=None):
    return render(request, "erro.html", {"codigo": 403, "titulo": "Acesso restrito",
                                         "mensagem": "Esta área é exclusiva da equipe da loja."}, status=403)


def erro_servidor(request):
    return render(request, "erro.html", {"codigo": 500, "titulo": "Algo deu errado",
                                         "mensagem": "Tivemos um problema do nosso lado. Tente novamente em instantes."}, status=500)

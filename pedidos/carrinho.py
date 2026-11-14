"""Carrinho de compras guardado na sessão (US09).

Guarda apenas {produto_id: quantidade}; preço e disponibilidade são sempre
lidos do banco (RN06: total calculado no servidor).
"""
from dataclasses import dataclass
from decimal import Decimal

from catalogo.models import Produto

CHAVE_SESSAO = "carrinho"
QTD_MAXIMA_POR_ITEM = 50


class ErroCarrinho(Exception):
    """Operação inválida no carrinho; a mensagem é exibida ao usuário."""


@dataclass(frozen=True)
class LinhaCarrinho:
    produto: Produto
    quantidade: int

    @property
    def total(self) -> Decimal:
        return self.produto.preco * self.quantidade


class Carrinho:
    def __init__(self, sessao):
        self.sessao = sessao
        self._itens: dict[str, int] = dict(sessao.get(CHAVE_SESSAO, {}))

    def _salvar(self):
        self.sessao[CHAVE_SESSAO] = self._itens
        self.sessao.modified = True

    def adicionar(self, produto: Produto, quantidade: int = 1) -> None:
        if quantidade < 1:
            raise ErroCarrinho("A quantidade deve ser pelo menos 1.")
        if not produto.disponivel:
            raise ErroCarrinho(f"{produto.nome} não está disponível no momento.")
        nova = self._itens.get(str(produto.pk), 0) + quantidade
        self._validar_quantidade(produto, nova)
        self._itens[str(produto.pk)] = nova
        self._salvar()

    def atualizar(self, produto: Produto, quantidade: int) -> None:
        if quantidade <= 0:
            self.remover(produto)
            return
        self._validar_quantidade(produto, quantidade)
        self._itens[str(produto.pk)] = quantidade
        self._salvar()

    def remover(self, produto: Produto) -> None:
        self._itens.pop(str(produto.pk), None)
        self._salvar()

    def limpar(self) -> None:
        self._itens = {}
        self._salvar()

    @staticmethod
    def _validar_quantidade(produto: Produto, quantidade: int) -> None:
        if quantidade > QTD_MAXIMA_POR_ITEM:
            raise ErroCarrinho(f"Máximo de {QTD_MAXIMA_POR_ITEM} unidades por item.")
        if quantidade > produto.estoque:
            raise ErroCarrinho(f"Só temos {produto.estoque} unidade(s) de {produto.nome} hoje.")

    def linhas(self) -> list[LinhaCarrinho]:
        """Linhas válidas; itens que ficaram indisponíveis são descartados."""
        ids = [int(i) for i in self._itens]
        produtos = Produto.objects.select_related("categoria").filter(pk__in=ids)
        linhas = [LinhaCarrinho(p, self._itens[str(p.pk)]) for p in produtos if p.disponivel]
        if len(linhas) != len(self._itens):
            self._itens = {str(l.produto.pk): l.quantidade for l in linhas}
            self._salvar()
        return sorted(linhas, key=lambda l: l.produto.nome)

    @property
    def quantidade_total(self) -> int:
        return sum(self._itens.values())

    def subtotal(self) -> Decimal:
        return sum((l.total for l in self.linhas()), Decimal("0"))

    def __len__(self):
        return len(self._itens)

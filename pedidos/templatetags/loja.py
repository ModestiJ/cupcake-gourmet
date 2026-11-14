from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

CORES_STATUS = {
    "RECEBIDO": "selo-ambar",
    "EM_PREPARO": "",
    "SAIU_PARA_ENTREGA": "",
    "PRONTO_RETIRADA": "",
    "ENTREGUE": "selo-menta",
    "CANCELADO": "selo-neutro",
    "PENDENTE": "selo-ambar",
    "APROVADO": "selo-menta",
    "RECUSADO": "selo-erro",
    "ESTORNADO": "selo-neutro",
}


@register.filter
def brl(valor) -> str:
    """Formata como moeda brasileira: 1234.5 -> 'R$ 1.234,50'."""
    try:
        v = Decimal(valor or 0).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return ""
    inteiro, dec = f"{abs(v):,.2f}".split(".")
    sinal = "-" if v < 0 else ""
    return f"{sinal}R$ {inteiro.replace(',', '.')},{dec}"


@register.filter
def cor_status(status: str) -> str:
    return CORES_STATUS.get(status, "")

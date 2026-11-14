"""Integração de pagamento (US13, US14) – padrão Strategy.

O sistema conversa com `GatewayPagamento`; hoje a implementação é
`GatewaySimulado`. Trocar por Mercado Pago/Stripe exige apenas uma nova
classe com o mesmo contrato, sem alterar services ou views.
"""
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class ResultadoCobranca:
    aprovado: bool
    transacao_ref: str
    mensagem: str


class GatewayPagamento(Protocol):
    def cobrar(self, valor: Decimal, metodo: str, referencia: str) -> ResultadoCobranca: ...

    def estornar(self, transacao_ref: str) -> bool: ...

    def codigo_pix(self, valor: Decimal, referencia: str) -> str: ...


class GatewaySimulado:
    """Gateway de demonstração. Nenhum dado de cartão é coletado (LGPD/RNF07).

    `recusar=True` simula uma recusa da operadora, para que testadores possam
    exercitar o caminho de erro pela interface ("Simular pagamento recusado").
    """

    def __init__(self, recusar: bool = False):
        self.recusar = recusar

    def cobrar(self, valor: Decimal, metodo: str, referencia: str) -> ResultadoCobranca:
        if valor <= 0:
            return ResultadoCobranca(False, "", "Valor inválido para cobrança.")
        ref = f"SIM-{metodo}-{uuid.uuid4().hex[:12].upper()}"
        if self.recusar:
            return ResultadoCobranca(False, ref, "Pagamento recusado pela operadora (simulado).")
        return ResultadoCobranca(True, ref, "Pagamento aprovado.")

    def estornar(self, transacao_ref: str) -> bool:
        return bool(transacao_ref)

    def codigo_pix(self, valor: Decimal, referencia: str) -> str:
        return f"00020126PIXSIMULADO-CUPCAKEGOURMET-{referencia}-{valor:.2f}-6304ABCD"


_gateway: GatewayPagamento = GatewaySimulado()


def obter_gateway() -> GatewayPagamento:
    return _gateway

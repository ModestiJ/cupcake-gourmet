# Laudo de qualidade – Cupcake Gourmet v1.0

> Preencha as seções marcadas com ✏️ depois de coletar os 5 laudos dos testadores.

## 1. Identificação

| | |
|---|---|
| Sistema | Cupcake Gourmet – vitrine, pedidos, pagamento e entrega |
| Versão avaliada | 1.0 (commit ✏️ `________`) |
| URL | ✏️ |
| Responsável | ✏️ Nome – RGM |
| Período de testes | ✏️ __/__/2026 a __/__/2026 |

## 2. Evidências da verificação automatizada

| Indicador | Resultado | Meta | Situação |
|---|---|---|---|
| Testes automatizados | 83/83 passando | 100% | ✅ |
| Cobertura de código | 94% | ≥ 70% (RNF06) | ✅ |
| Cobertura das regras de negócio (`services.py`) | 98% | ≥ 70% | ✅ |
| Histórias implementadas | 17/18 (US18 adiada para a v2) | Must + Should | ✅ |
| `check --deploy` (segurança Django) | sem erros. Avisos de HSTS em subdomínio não se aplicam ao domínio do Render. | sem erros | ✅ |
| CI em PostgreSQL (GitHub Actions) | ✏️ link do run verde | verde | |

## 3. Resultado da validação com testadores ✏️

| # | Testador | Data | Funcionou | Não funcionou | Não testado | Nota geral |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

## 4. Defeitos e sugestões consolidados ✏️

| ID | Origem (testador) | Descrição | Gravidade | Decisão | Correção aplicada (commit) | Evidência |
|---|---|---|---|---|---|---|
| B01 | | | | Corrigir / Adiar / Não procede | | print antes/depois |
| S01 | | (sugestão) | — | | | |

**Critério de decisão:** defeitos de gravidade alta ou média são corrigidos nesta versão. Sugestões entram se forem compatíveis com o escopo e com o prazo. As demais vão para o backlog da v2, com justificativa.

## 5. Defeitos encontrados internamente (antes dos testadores)

| ID | Descrição | Correção |
|---|---|---|
| D1 | Teste de limite de quantidade com expectativa errada | Teste corrigido para cobrir o estoque e o limite por item |
| D2 | *Open redirect* no parâmetro `next` | `destino_seguro()` + teste automatizado |
| D3 | Recusa de pagamento simulada impossível de reproduzir | Botão "Simular pagamento recusado" + teste |

## 6. Conclusão ✏️

_Ex.: "O sistema atende aos requisitos Must e Should do backlog. Dos N problemas relatados, X foram corrigidos (lista), Y adiados para a v2 (lista e motivo). O produto está apto para demonstração."_

## 7. Backlog da v2
- US18 – aviso por e-mail quando o pedido sai para entrega
- Integração com um gateway real (Mercado Pago), implementando a interface `GatewayPagamento`
- Upload de fotos reais dos produtos (armazenamento em nuvem)
- ✏️ sugestões dos testadores adiadas

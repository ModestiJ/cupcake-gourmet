# Laudo de qualidade – Cupcake Gourmet v1.0

## 1. Identificação

| | |
|---|---|
| Sistema | Cupcake Gourmet – vitrine, pedidos, pagamento e entrega |
| Versão avaliada | 1.0, publicada em produção em 14/11/2026. As correções desta validação estão em `386a74f`, `836ae3e` e `c57d159`. |
| URL | https://cupcake-gourmet-2uvn.onrender.com |
| Responsável | João Pedro Andrade Modesti |
| Período de testes | 14/11/2026 a 15/11/2026 |

## 2. Evidências da verificação automatizada

| Indicador | Resultado | Meta | Situação |
|---|---|---|---|
| Testes automatizados | 105/105 passando | 100% | ✅ |
| Cobertura de código | 94% | ≥ 70% (RNF06) | ✅ |
| Cobertura das regras de negócio (`services.py`) | 98% | ≥ 70% | ✅ |
| Histórias implementadas | 17/18 (US18 adiada para a v2) | Must + Should | ✅ |
| `check --deploy` (segurança Django) | sem erros. Avisos de HSTS em subdomínio não se aplicam ao domínio do Render. | sem erros | ✅ |
| CI em PostgreSQL (GitHub Actions) | 105/105 passando ([run](https://github.com/ModestiJ/cupcake-gourmet/actions/runs/43713289570)) | verde | ✅ |
| Teste de sistema E2E em produção (`scripts/smoke_prod.py`) | 23/23 verificações, executado de novo após cada correção | 100% | ✅ |

## 3. Resultado da validação com testadores

**7 pessoas** responderam ao formulário em 14/11/2026: 2 profissionais de TI e 5 usuários finais, em celular Android, iPhone e computador. Respostas completas em [laudos/respostas-dos-testadores.md](laudos/respostas-dos-testadores.md). Por privacidade, o repositório usa nomes abreviados; os nomes completos estão no PDF entregue ao tutor.

| # | Testador | Perfil | Funcionou | Não funcionou | Não testado | Nota geral |
|---|---|---|---|---|---|---|
| 1 | Luciano F. | Profissional de TI | 12 de 16 funcionalidades | nada (sugestão B07) | F04, F06, F14, F15 | 4 |
| 2 | Augusto W. | Profissional de TI | 8 de 16 | busca com acentos + prints B02–B05 | F06, F08, F10–F15 | 5 |
| 3 | João B. | Usuário final | 9 de 16 | nada (sugestão S01) | F03, F04, F08, F11, F13–F15 | 5 |
| 4 | Verônica M. | Usuário final | 14 de 16 | nada | F14, F15 (admin) | 5 |
| 5 | Henrique M. | Usuário final | 14 de 16 | nada | F14, F15\* | 5 |
| 6 | Jiliana A. | Usuário final | 14 de 16 | nada | F14, F15\* | 5 |
| 7 | Cleber M. | Usuário final | 14 de 16 | nada | F14, F15\* | 5 |

**Médias (1 a 5):** facilidade de uso **5,0** · visual **4,57** · velocidade **4,57** · nota geral **4,86**.

\* Esses testadores marcaram o painel de administrador como “funcionou”, mas **não receberam login de administrador**. Os itens foram considerados **não testados**, para não registrar um teste que não aconteceu. O painel foi verificado pelos testes automatizados (US07, US12 e US15) e pelo roteiro de sistema do responsável.

Nenhuma funcionalidade foi marcada como “não funcionou”. Todas as 16 foram testadas por pelo menos um testador, exceto o painel de administrador, que nenhum testador externo pôde testar.

## 4. Defeitos e sugestões consolidados

| ID | Origem | Descrição | Gravidade | Decisão | Correção (commit) | Evidência |
|---|---|---|---|---|---|---|
| B01 | Eduardo (relato por WhatsApp, com captura de tela; não respondeu ao formulário) | Erro 500 (“Algo deu errado”) ao criar conta no iPhone (Chrome), logo após a mensagem de senha curta. Causa: envio duplicado do formulário (D6). | Alta | Corrigir | `386a74f` | print do erro + log do Render + teste de regressão |
| B02 | Augusto W. | Não há onde alterar a senha na tela Minha conta | Média | Corrigir | `c57d159` | print da tela + `test_b02_*` |
| B03 | Augusto W. | Sugestão: contador de unidades no carrinho | Baixa | Corrigir | `c57d159` | print antes/depois + `test_b03_*` |
| B04 | Augusto W. | Hero colado no cabeçalho, sem margem. Causa: `.container` zerava o `padding-top` do `main` em **todas** as páginas (especificidade CSS) | Baixa | Corrigir | `c57d159` | print antes/depois + `test_b04_*` |
| B05 | Augusto W. | Pouco respiro entre o aviso (toast) e o conteúdo | Baixa | Corrigir (mesma causa do B04) | `c57d159` | print antes/depois |
| B06 | Augusto W. (formulário e prints) | Busca por “Verao” não encontra “Blueberry de Verão” (acentos) | Média | Corrigir: busca e bairro de entrega passam a ignorar acentos e maiúsculas | `c57d159` | print antes/depois + `test_b06_*` |
| B07 | Luciano F. | Sugestão: mais resposta visual a cliques e ações; “em alguns momentos pareceu lento” (nota 3 em velocidade) | Baixa | **Adiar (v2)**. A lentidão ocorre principalmente no 1º acesso, por causa da hibernação do plano gratuito (Render ~50 s, Neon ~1 s). Já existe mitigação parcial: os botões travam após o 1º toque (correção do B01). | — | resposta do formulário |
| S01 | João B. | Sugestão: tela de ofertas/promoções (nota 3 em visual) | — | **Adiar (v2)**. Exige preço promocional com vigência, fora do escopo atual. A vitrine já tem “Destaques do dia”. | — | resposta do formulário |

**Critério de decisão:** defeitos de gravidade alta ou média são corrigidos nesta versão. Sugestões entram se forem compatíveis com o escopo e com o prazo. As demais vão para o backlog da v2, com justificativa.

## 5. Defeitos encontrados internamente

| ID | Descrição | Correção |
|---|---|---|
| D1 | Teste de limite de quantidade com expectativa errada | Teste corrigido para cobrir o estoque e o limite por item |
| D2 | *Open redirect* no parâmetro `next` | `destino_seguro()` + teste automatizado |
| D3 | Recusa de pagamento simulada impossível de reproduzir | Botão "Simular pagamento recusado" + teste |
| D5 | Avançar e cancelar pedido falhavam no PostgreSQL (lock em LEFT JOIN), sem aparecer no SQLite | `select_for_update(of=("self",))`. Detectado pelo CI em Postgres. |
| D7 | Login diferenciava maiúsculas no e-mail (o celular capitaliza a 1ª letra). Encontrado ao investigar o B01. | E-mail normalizado no login (`836ae3e`) + teste |

## 6. Conclusão

O sistema atende às histórias **Must e Should** do backlog (17 de 18 histórias). Na validação, **7 testadores** avaliaram o produto com nota geral média de **4,86 de 5**, e nenhum marcou funcionalidade como “não funcionou”. Foram relatados **6 defeitos ou ajustes** (B01–B06), **todos corrigidos**, com teste de regressão automatizado e verificação em produção. Ao investigar o B01 apareceu mais um defeito (D7), também corrigido. As **2 sugestões** não incorporadas (B07 e S01) foram registradas no backlog da v2, com justificativa. Não há defeito conhecido em aberto, e o produto está apto para demonstração.

Limitações conhecidas: o painel de administrador não teve validação por testador externo (só pelos testes automatizados e pelo responsável). No plano gratuito, o primeiro acesso após inatividade pode levar até ~50 s.

## 7. Backlog da v2
- US18 – aviso por e-mail quando o pedido sai para entrega
- B07 – indicador de carregamento em botões e links; hospedagem sem hibernação (plano pago ou *keep-alive*)
- S01 – ofertas/promoções com preço promocional e vigência
- Integração com um gateway real (Mercado Pago), implementando a interface `GatewayPagamento`
- Upload de fotos reais dos produtos (armazenamento em nuvem)
- Recuperação de senha por e-mail (“esqueci minha senha”)
- Validação do painel de administrador por um testador externo com acesso próprio

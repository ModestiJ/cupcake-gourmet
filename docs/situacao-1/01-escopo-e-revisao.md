# Situação 1 · Escopo e revisão do PIT I

## 1. Contexto

No **PIT I** foi produzida a especificação ágil de um aplicativo para uma **loja de cupcakes gourmet** (briefing "Stands ou Loja de Cupcakes"). O trabalho entregou:

- 18 histórias de usuário;
- mapa de afinidade com 5 temas: Autenticação, Vitrine, Pedido, Pagamento e Entrega;
- backlog priorizado com MoSCoW e pontos em Fibonacci;
- critérios de aceitação em Gherkin;
- requisito não funcional "RNf1 – app responsivo mobile".

No **PIT II** essa especificação vira um produto funcionando. Antes de codificar, aplicamos um ciclo de melhoria contínua (*Kaizen*) sobre o planejamento.

## 2. Problema e objetivo

| | |
|---|---|
| **Problema** | A loja vende só no balcão e por mensagens. Pedidos se perdem, não há controle de estoque diário e o cliente não sabe o status da encomenda. |
| **Objetivo** | Oferecer uma vitrine virtual onde o cliente escolhe cupcakes, faz o pedido (entrega ou retirada), paga e acompanha o status, e um painel onde a loja gerencia produtos, estoque e a fila de pedidos. |
| **Personas** | **Cliente** (compra pelo celular) e **Administrador** (dono ou atendente da loja). |
| **Fora do escopo (v1)** | Gateway de pagamento real, notificações por e-mail/push, app nativo nas lojas, cupons e programa de fidelidade. |

## 3. Revisão do PIT I (Kaizen)

| # | Situação no PIT I | Problema encontrado | Ação no PIT II |
|---|---|---|---|
| 1 | O documento só resume as 18 histórias | Sem as histórias completas não há rastreabilidade entre requisito, código e teste | Histórias reescritas com ID, critérios Gherkin, regras e prioridade ([02-requisitos.md](02-requisitos.md)) |
| 2 | "App mobile" sem plataforma definida | O PIT II exige front em HTML/CSS/JS, e um app nativo dobraria o esforço | **Web responsiva mobile-first + PWA** (instalável no celular). Atende ao RNf1 com um único código. |
| 3 | Pagamento previsto como integração real | Exige CNPJ, credenciamento e homologação, inviável no prazo | **Gateway simulado** atrás de uma interface (padrão Strategy). Trocar por Mercado Pago/Stripe não altera as regras. |
| 4 | Sem modelagem UML | A disciplina exige casos de uso, classes, sequência e atividades | Diagramas em [03-uml.md](03-uml.md) |
| 5 | Sem protótipo de telas nem mensagens de erro | A IHC não tinha sido definida | Mapa de navegação, heurísticas e catálogo de mensagens em [04-ihc.md](04-ihc.md). As telas implementadas são o protótipo de alta fidelidade. |
| 6 | Sem modelo de dados | Faltavam regras de integridade | Modelos conceitual, lógico (3FN) e físico, mais o dicionário de dados ([05-banco-de-dados.md](05-banco-de-dados.md)) |
| 7 | Regras de negócio implícitas nas histórias | Ambiguidade (ex.: quando o cliente pode cancelar?) | Regras explícitas RN01–RN08 |
| 8 | Só 1 RNF | Faltavam segurança, LGPD, desempenho e testabilidade | RNF01–RNF08 |
| 9 | US "notificação de saída para entrega" priorizada como Should | Depende de um provedor de e-mail. A linha do tempo (US17) já resolve a dor de "não sei onde está meu pedido". | Reclassificada como **Won't (v2)** |

## 4. Decisões de tecnologia

| Item | Escolha | Justificativa |
|---|---|---|
| Linguagem back-end | **Python 3.14** | Linguagem aceita pela disciplina e de domínio do autor |
| Framework | **Django 6** (MVC/MTV) | ORM com migrations, autenticação, CSRF e formulários prontos. Menos código de infraestrutura e mais foco nas regras. |
| Front-end | HTML5 + CSS3 + JavaScript puro (templates server-side) | Pedido explícito da disciplina. Sem framework de build, o que deixa o projeto mais leve e acessível. |
| SGBD | **PostgreSQL** (Neon) em produção, SQLite em desenvolvimento | SGBD popular e robusto, conforme a orientação de "nada de SGBD obscuro" |
| Testes | **pytest** + pytest-django + coverage | Indicado no material da disciplina |
| Hospedagem | **Render** (web) + **Neon** (Postgres) | Planos gratuitos com HTTPS e deploy automático a partir do GitHub |
| Modo de codificação | **Tradicional** | |

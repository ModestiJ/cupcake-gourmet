# Roteiro – vídeo narrado da solução (≥ 5 min)

Grave a tela com OBS ou com a Barra de Jogos do Windows (Win+Alt+R). Deixe duas abas abertas: uma anônima (cliente) e uma normal (admin). Mostre também o celular, ou o DevTools em modo dispositivo (F12 → Ctrl+Shift+M).

| Tempo | Cena | O que mostrar / falar |
|---|---|---|
| 0:00–0:30 | Abertura | Seu nome e RGM. "Este é o Cupcake Gourmet, a implementação da especificação ágil do PIT I: vitrine, pedido, pagamento e entrega para uma loja de cupcakes." |
| 0:30–1:00 | Repositório | GitHub: as pastas `docs/situacao-1, 2, 3`, o código MVC e o selo dos testes passando no Actions |
| 1:00–1:45 | Vitrine (celular) | Destaques, filtro por categoria, busca por "pistache", detalhe com ingredientes e estoque. Comentar o mobile-first e o PWA. |
| 1:45–2:30 | Carrinho e conta | Adicionar 2 sabores, alterar a quantidade, tentar exceder o estoque (mensagem de erro). Criar conta (mostrar a validação de senha e o aceite LGPD). |
| 2:30–3:30 | Checkout | Endereço em bairro atendido (taxa) e em bairro não atendido (desabilitado). Total recalculado. Confirmar com Pix e mostrar o código copia e cola. Confirmar o pagamento. |
| 3:30–4:30 | Painel admin | Indicadores do dia, alerta de estoque, fila. Tentar avançar um pedido Pix não pago (RN08 bloqueia). Avançar o pedido pago até "Entregue". |
| 4:30–5:00 | Acompanhamento | Voltar à aba do cliente: linha do tempo completa. Mostrar o cancelamento em outro pedido "Recebido" e o estoque voltando. |
| 5:00–5:40 | Cadastros | Criar um cupcake novo e mostrar que ele aparece na vitrine. Excluir um produto com pedidos (vira desativado). |
| 5:40–6:30 | Qualidade | Terminal: `coverage run -m pytest` mostrando 83 testes passando e 94% de cobertura. Explicar rapidamente MVC + services + Strategy de pagamento. |
| 6:30–7:00 | Encerramento | Próximos passos (gateway real, notificação por e-mail – US18) e convite para testar pelo link. |

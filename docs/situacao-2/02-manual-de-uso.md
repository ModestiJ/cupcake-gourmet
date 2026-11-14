# Manual de uso – Cupcake Gourmet

**Acesse:** https://cupcake-gourmet-2uvn.onrender.com

> **Ambiente de demonstração.** Os pagamentos são simulados e nenhum dado de cartão é pedido. Pedidos não geram cobrança nem entrega reais.
> No plano gratuito do Render, o primeiro acesso após um tempo parado pode levar até ~50 s para "acordar" o servidor.

## Contas de teste

| Perfil | E-mail | Senha |
|---|---|---|
| Cliente | `cliente@cupcake.dev` | `Cliente@123` |
| Administrador | informado ao tutor/testadores em privado | — |

Você também pode criar sua própria conta em **Entrar → Cadastre-se**.

## Instalar como app no celular (opcional)

- **Android/Chrome:** menu ⋮ → **Adicionar à tela inicial**.
- **iPhone/Safari:** botão Compartilhar → **Adicionar à Tela de Início**.

---

## Parte A – Cliente

### 1. Vitrine
- A página inicial mostra os **Destaques do dia** e todos os sabores.
- Toque numa **categoria** (Clássicos, Gourmet, Veganos, Sazonais) para filtrar.
- Use a **busca** para procurar por nome, sabor ou ingrediente (ex.: "pistache").
- Toque no cupcake para ver descrição, ingredientes e estoque do dia.

### 2. Carrinho
- Toque em **+ 🛒** no card, ou escolha a quantidade no detalhe e toque em **Adicionar ao carrinho**.
- No **Carrinho**, use − / + para mudar a quantidade (salva sozinho) ou **Remover**.
- O número ao lado do ícone 🛒 mostra quantos itens há no carrinho.

### 3. Finalizar pedido
1. Toque em **Finalizar pedido**. Se não estiver logado, entre ou crie sua conta.
2. **Como quer receber?** Escolha *Entrega* ou *Retirar na loja* (sem taxa).
3. **Endereço:** cada endereço mostra a taxa do bairro. Bairros não atendidos aparecem desabilitados. Use **+ Adicionar endereço** se precisar. A lista de bairros está em **Áreas de entrega**, no rodapé.
4. **Pagamento:** Pix, Cartão (online) ou Pagar na entrega/retirada.
5. Confira o **total** (atualizado na hora) e toque em **Confirmar pedido**.

### 4. Pagamento (simulado)
- **Pix:** aparece um QR ilustrativo e o código "copia e cola". Toque em **Já paguei – confirmar (simulação)**.
- **Cartão:** toque em **Pagar (simulação)**.
- Para testar uma **recusa**, toque em **Simular pagamento recusado (teste)**. O sistema mostra a mensagem de recusa e deixa tentar de novo.
- Também dá para **pagar depois** pelo detalhe do pedido (botão *Pagar agora*).

### 5. Acompanhar e cancelar
- Em **Pedidos** (barra inferior) ficam todos os seus pedidos com status e total.
- No detalhe, a **linha do tempo** mostra cada etapa com data e hora.
- Enquanto o pedido estiver **Recebido**, você pode **Cancelar pedido**. Depois que a loja inicia o preparo, o cancelamento só pode ser feito pela loja.

### 6. Minha conta
- Em **Conta**, altere nome e telefone, e cadastre, edite ou remova endereços. Marque um como **principal** para ele vir selecionado no checkout.

---

## Parte B – Administrador da loja

Ao entrar com uma conta de administrador, você vai direto para o **Painel**.

### 1. Painel de pedidos
- **Indicadores do dia:** quantidade de pedidos, valor vendido, ticket médio e pedidos em aberto (cancelados não contam).
- **Alerta de estoque baixo** (5 unidades ou menos), com link para editar o produto.
- **Fila de pedidos** (os mais antigos primeiro). Cada card mostra cliente, itens, tipo de entrega e situação do pagamento.
- O botão **→ Próxima etapa** avança o status: Recebido → Em preparo → Saiu para entrega (ou Pronto para retirada) → Entregue.
  - Pedidos com Pix/cartão **não pagos** não podem ir para preparo.
  - Pedidos "pagar na entrega" são marcados como pagos ao serem entregues.
- Use o filtro para ver todos os pedidos ou um status específico.
- No detalhe do pedido você vê os dados do cliente, a referência do pagamento e a linha do tempo, e pode **cancelar** o pedido (o estoque volta e o pagamento aprovado é estornado).

### 2. Cupcakes, categorias e zonas de entrega
- Use as abas 🧁 **Cupcakes**, 🏷️ **Categorias** e 🛵 **Zonas de entrega**.
- **+ Novo** cria um registro. Clique no nome para editar.
- **Estoque** = unidades disponíveis hoje. Com 0, o cupcake some da vitrine.
- **Destaque** coloca o cupcake em "Destaques do dia".
- **Excluir:** se o item já tiver pedidos (ou a categoria tiver produtos), ele é **desativado** em vez de excluído, para preservar o histórico.

### 3. Administração avançada
- `/django-admin/` dá acesso total aos dados (apenas superusuário).

---

## Para desenvolvedores

Veja o [README](../../README.md) para rodar localmente, executar os testes e fazer o deploy.

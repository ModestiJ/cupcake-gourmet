# Manual de uso – Cupcake Gourmet

**Acesse:** https://cupcake-gourmet-2uvn.onrender.com

> **Ambiente de demonstração.** Os pagamentos são simulados e nenhum dado de cartão é solicitado. Os pedidos não geram cobrança nem entrega reais.
>
> O servidor gratuito "dorme" quando fica sem uso. Se o primeiro acesso demorar, aguarde até 50 segundos.

## Contas de teste

| Perfil | E-mail | Senha |
|---|---|---|
| Cliente | `cliente@cupcake.dev` | `Cliente@123` |
| Administrador | enviado em particular para quem for testar o painel | — |

Se preferir, crie a sua própria conta: toque em **Entrar** e depois em **Cadastre-se**.

## Onde fica cada coisa

| | No celular | No computador |
|---|---|---|
| Vitrine | barra inferior → 🧁 **Vitrine** | topo → **Vitrine** |
| Carrinho | barra inferior → 🛒 **Carrinho** | topo → ícone 🛒 |
| Meus pedidos | barra inferior → 📦 **Pedidos** | topo → **Meus pedidos** |
| Minha conta e sair | barra inferior → 👤 **Conta** | topo → **Olá, (seu nome)** / **Sair** |
| Bairros atendidos | rodapé → **Áreas de entrega** | rodapé → **Áreas de entrega** |

## Usar como aplicativo no celular (opcional)

- **Android (Chrome):** menu ⋮ → **Adicionar à tela inicial**.
- **iPhone (Safari):** botão Compartilhar → **Adicionar à Tela de Início**.

---

## Parte A – Cliente

### 1. Escolher os cupcakes
- A página inicial mostra os **Destaques do dia** e, logo abaixo, todos os sabores.
- Toque numa **categoria** (Clássicos, Gourmet, Veganos ou Sazonais) para filtrar. Para ver tudo de novo, toque em **Todos**.
- Use a **busca** para procurar por nome, sabor, ingrediente ou categoria (ex.: "pistache"). Acentos e maiúsculas não importam: "verao" encontra "Verão".
- Toque no cupcake para ver a descrição, os ingredientes e quantas unidades restam hoje.

### 2. Montar o carrinho
- Toque em **+ 🛒** no card do cupcake, ou escolha a quantidade na página do cupcake e toque em **Adicionar ao carrinho**.
- No **Carrinho**, use **−** e **+** para mudar a quantidade (a alteração é salva na hora) ou toque em **Remover**.
- O número ao lado do 🛒 mostra quantas unidades há no carrinho.
- Não é possível pedir mais unidades do que o estoque do dia, nem mais de 50 unidades do mesmo sabor. Se tentar, aparece um aviso.

### 3. Finalizar o pedido
1. No carrinho, toque em **Finalizar pedido**. Se você ainda não entrou na sua conta, o sistema pede o login (ou o cadastro) e depois volta para esta etapa.
2. **Como quer receber?** Escolha **Entrega** ou **Retirar na loja** (sem taxa).
3. **Endereço** (só para entrega): cada endereço mostra a taxa de entrega do bairro. Endereços em bairros que a loja ainda não atende aparecem bloqueados. Para cadastrar outro endereço, toque em **+ Adicionar endereço**.
4. **Pagamento:** escolha **Pix**, **Cartão (online)** ou **Pagar na entrega/retirada**.
5. Confira o **total**, que já inclui a taxa de entrega e muda conforme as suas escolhas, e toque em **Confirmar pedido**.

### 4. Pagar (simulação)
- **Pix:** aparecem um QR Code ilustrativo e o código "copia e cola". Toque em **Já paguei – confirmar (simulação)**.
- **Cartão:** toque em **Pagar R$ … (simulação)**. Nenhum dado de cartão é pedido.
- **Testar um pagamento recusado:** toque em **Simular pagamento recusado (teste)**. O sistema mostra o aviso de recusa e permite tentar de novo.
- Também dá para **pagar depois**: abra o pedido e toque em **Pagar agora**.
- Se você escolheu **Pagar na entrega/retirada**, não há etapa de pagamento. O pedido já vai direto para acompanhamento.

### 5. Acompanhar e cancelar
- Em **Pedidos** (ou **Meus pedidos**, no computador) ficam todos os seus pedidos, com a situação e o total.
- Ao abrir um pedido, a **linha do tempo** mostra cada etapa com data e hora: Recebido → Em preparo → Saiu para entrega (ou Pronto para retirada) → Entregue.
- Enquanto o pedido estiver **Recebido**, você pode tocar em **Cancelar pedido**. Depois que a loja começa o preparo, só a loja pode cancelar.

### 6. Minha conta
- Em **Conta** você altera o nome e o telefone, e cadastra, edita ou remove endereços.
- Marque um endereço como **principal** para que ele já venha selecionado ao finalizar o pedido.
- Para trocar a senha, toque em **🔑 Alterar senha** (informe a senha atual e a nova duas vezes).
- Para sair, toque em **Sair**.

---

## Parte B – Administrador da loja

Ao entrar com uma conta de administrador, você vai direto para o **Painel**.

### 1. Painel de pedidos
- No topo ficam os **números do dia**: pedidos, valor vendido, ticket médio e pedidos em aberto. Pedidos cancelados não entram na conta.
- Um **alerta de estoque baixo** aparece quando um cupcake tem 5 unidades ou menos. Toque no nome para ajustar o estoque.
- A **fila de pedidos** mostra primeiro os pedidos mais antigos, com o cliente, os itens, o tipo de entrega e a situação do pagamento.
- O botão de cada pedido mostra a **próxima etapa** (ex.: **→ Em preparo**, **→ Saiu para entrega**, **→ Entregue**). Toque para avançar.
  - Pedidos com Pix ou cartão **ainda não pagos** não podem ir para preparo. O sistema avisa.
  - Pedidos "pagar na entrega/retirada" são marcados como pagos quando você confirma a entrega.
- Use o filtro acima da fila para ver todos os pedidos ou só os de uma situação.
- Toque no número do pedido para ver os detalhes: dados do cliente, endereço, referência do pagamento e linha do tempo. Ali também é possível **cancelar** o pedido. O estoque volta e o pagamento aprovado é estornado.

### 2. Cupcakes, categorias e zonas de entrega
- Use as abas 🧁 **Cupcakes**, 🏷️ **Categorias** e 🛵 **Zonas de entrega**.
- **+ Novo** cria um cadastro. Toque no nome para editar.
- **Estoque** é a quantidade disponível hoje. Com estoque zero, o cupcake sai da vitrine automaticamente.
- **Destaque** coloca o cupcake na seção "Destaques do dia".
- **Excluir:** se o cupcake já aparece em algum pedido, ou se a categoria ainda tem cupcakes, o registro é **desativado** em vez de apagado, para não perder o histórico.

### 3. Administração avançada
- O endereço `/django-admin/` dá acesso completo aos dados (só para o superusuário).

---

## Para desenvolvedores

Veja o [README](../../README.md) para rodar o projeto localmente, executar os testes e publicar.

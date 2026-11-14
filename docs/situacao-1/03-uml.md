# Situação 1 · Modelagem UML

Os diagramas estão em Mermaid, que o GitHub renderiza automaticamente. Eles foram revisados para refletir **exatamente** o código entregue.

## 1. Diagrama de casos de uso

```mermaid
flowchart LR
    V([Visitante])
    C([Cliente])
    A([Administrador])
    G[[Gateway de pagamento<br/>simulado]]

    subgraph Sistema["Sistema Cupcake Gourmet"]
        UC1((Ver vitrine por categoria))
        UC2((Buscar cupcake))
        UC3((Ver detalhes))
        UC4((Gerenciar carrinho))
        UC5((Criar conta))
        UC6((Entrar / Sair))
        UC7((Gerenciar perfil e endereços))
        UC8((Finalizar pedido))
        UC9((Calcular taxa de entrega))
        UC10((Pagar pedido))
        UC11((Acompanhar pedido))
        UC12((Cancelar pedido))
        UC13((Gerenciar cupcakes))
        UC14((Gerenciar categorias))
        UC15((Gerenciar zonas de entrega))
        UC16((Avançar status do pedido))
        UC17((Ver resumo de vendas))
    end

    V --> UC1 & UC2 & UC3 & UC4 & UC5
    C --> UC6 & UC7 & UC8 & UC10 & UC11 & UC12
    C -.herda.-> V
    A --> UC6 & UC13 & UC14 & UC15 & UC16 & UC12 & UC17
    UC8 -. include .-> UC9
    UC8 -. extend .-> UC10
    UC10 --> G
    UC12 -. include: estorno .-> G
```

### Descrição do caso de uso principal: UC8 Finalizar pedido

| Campo | Descrição |
|---|---|
| Ator | Cliente (autenticado) |
| Pré-condições | Carrinho com pelo menos 1 item disponível |
| Fluxo principal | 1. O cliente abre o checkout. 2. O sistema mostra os itens, os endereços com a taxa de cada bairro e as formas de pagamento. 3. O cliente escolhe entrega/retirada, endereço e pagamento. 4. O sistema recalcula o total ao vivo. 5. O cliente confirma. 6. O sistema trava o estoque, valida a disponibilidade, cria o pedido com os preços congelados, baixa o estoque, registra o pagamento PENDENTE e o histórico RECEBIDO, e esvazia o carrinho. 7. Se o pagamento for online, redireciona para a tela de pagamento. Se não, para o detalhe do pedido. |
| Fluxos alternativos | **A1** Bairro não atendido: o endereço aparece desabilitado e o cliente pode escolher retirada. **A2** Sem endereço: o cliente cadastra um e volta ao checkout. **A3** Item esgotou entre o carrinho e a confirmação: a transação é desfeita e aparece "X acabou de esgotar. Ajuste seu carrinho." |
| Pós-condições | Pedido em `RECEBIDO`, estoque baixado e carrinho vazio |
| Regras | RN01, RN02, RN05, RN06 |

## 2. Diagrama de classes (domínio e persistência)

```mermaid
classDiagram
    direction LR
    class Usuario {
      +id: bigint
      +nome: str
      +email: str «unique»
      +telefone: str
      +perfil: CLIENTE|ADMIN
      +password: hash
      +criado_em: datetime
      +is_admin_loja() bool
    }
    class Endereco {
      +apelido: str
      +logradouro: str
      +numero: str
      +complemento: str
      +bairro: str
      +cidade: str
      +cep: str
      +principal: bool
    }
    class Categoria {
      +nome: str «unique»
      +slug: str «unique»
      +ativa: bool
      +ordem: int
    }
    class Produto {
      +nome: str
      +descricao: text
      +ingredientes: str
      +preco: decimal «> 0»
      +estoque: int «>= 0»
      +imagem: str
      +ativo: bool
      +destaque: bool
      +disponivel() bool
    }
    class ZonaEntrega {
      +bairro: str «unique»
      +taxa: decimal «>= 0»
      +ativa: bool
    }
    class Pedido {
      +tipo_entrega: ENTREGA|RETIRADA
      +endereco_entrega: str
      +bairro: str
      +status: Status
      +subtotal: decimal
      +taxa_entrega: decimal
      +total: decimal
      +observacao: str
      +codigo() str
      +finalizado() bool
    }
    class ItemPedido {
      +nome_produto: str
      +quantidade: int «> 0»
      +preco_unitario: decimal
      +total() decimal
    }
    class Pagamento {
      +metodo: PIX|CARTAO|NA_ENTREGA
      +status: PENDENTE|APROVADO|RECUSADO|ESTORNADO
      +valor: decimal
      +transacao_ref: str
      +pago_em: datetime
      +liberado_para_preparo() bool
    }
    class HistoricoStatus {
      +status: Status
      +alterado_em: datetime
    }
    Usuario "1" *-- "0..*" Endereco
    Usuario "1" --> "0..*" Pedido : faz
    Categoria "1" o-- "0..*" Produto
    Pedido "1" *-- "1..*" ItemPedido
    ItemPedido "0..*" --> "1" Produto
    Pedido "1" *-- "1" Pagamento
    Pedido "1" *-- "1..*" HistoricoStatus
    HistoricoStatus "0..*" --> "0..1" Usuario : alterado_por
```

### Classes de serviço (camada de regras)

```mermaid
classDiagram
    class Carrinho {
      -sessao
      +adicionar(produto, qtd)
      +atualizar(produto, qtd)
      +remover(produto)
      +linhas() LinhaCarrinho[]
      +subtotal() Decimal
    }
    class PedidoService {
      <<module services.py>>
      +calcular_taxa(tipo, bairro) Decimal
      +criar_pedido(usuario, carrinho, tipo, metodo, endereco) Pedido
      +pagar_pedido(pedido, gateway) ResultadoCobranca
      +proximo_status(pedido) Status
      +avancar_status(pedido, admin) Pedido
      +cancelar_pedido(pedido, usuario, gateway) Pedido
      +resumo_vendas_do_dia() ResumoVendas
    }
    class GatewayPagamento {
      <<interface>>
      +cobrar(valor, metodo, ref) ResultadoCobranca
      +estornar(ref) bool
      +codigo_pix(valor, ref) str
    }
    class GatewaySimulado
    GatewayPagamento <|.. GatewaySimulado : realiza
    PedidoService ..> Carrinho
    PedidoService ..> GatewayPagamento : Strategy
```

## 3. Diagrama de sequência: finalizar pedido e pagar com Pix

```mermaid
sequenceDiagram
    actor C as Cliente
    participant V as View (templates)
    participant CT as Controller<br/>pedidos.views
    participant S as services
    participant M as Models (ORM)
    participant DB as PostgreSQL
    participant GW as GatewaySimulado

    C->>CT: POST /checkout (tipo, endereço, PIX)
    CT->>S: criar_pedido(usuario, carrinho, ...)
    S->>S: calcular_taxa(bairro)
    S->>M: SELECT ... FOR UPDATE (produtos)
    M->>DB: BEGIN; lock nas linhas
    loop cada item
        S->>S: valida estoque e disponibilidade
        S->>M: cria ItemPedido(preço congelado)
        S->>M: UPDATE estoque = estoque - qtd
    end
    S->>M: cria Pagamento(PENDENTE) e Historico(RECEBIDO)
    M->>DB: COMMIT
    S-->>CT: pedido
    CT-->>C: 302 → /pedidos/{id}/pagamento
    C->>CT: GET pagamento
    CT->>GW: codigo_pix(valor, ref)
    CT->>V: render pagamento.html
    V-->>C: QR + "copia e cola"
    C->>CT: POST pagamento (confirmar)
    CT->>S: pagar_pedido(pedido)
    S->>GW: cobrar(valor, PIX, ref)
    GW-->>S: ResultadoCobranca(aprovado)
    S->>M: Pagamento → APROVADO
    CT-->>C: 302 → detalhe + "Pagamento aprovado!"
```

## 4. Diagrama de atividades: ciclo do pedido

```mermaid
flowchart TD
    I((Início)) --> A[Cliente monta carrinho]
    A --> B{Logado?}
    B -- não --> L[Entrar / criar conta] --> C
    B -- sim --> C[Checkout]
    C --> D{Entrega ou retirada?}
    D -- Entrega --> E{Bairro atendido?}
    E -- não --> E2[Escolher outro endereço<br/>ou retirada] --> D
    E -- sim --> F[Somar taxa da zona]
    D -- Retirada --> F0[Taxa = 0]
    F --> G[Escolher pagamento]
    F0 --> G
    G --> H[Confirmar pedido<br/>status RECEBIDO]
    H --> P{Pagamento online?}
    P -- sim --> Q[Pagar Pix/Cartão]
    Q --> R{Aprovado?}
    R -- não --> Q
    R -- sim --> S
    P -- na entrega --> S[Admin: EM_PREPARO]
    H -. cliente cancela .-> X[CANCELADO<br/>devolve estoque/estorna]
    S --> T{Tipo}
    T -- Entrega --> U[SAIU_PARA_ENTREGA]
    T -- Retirada --> U2[PRONTO_RETIRADA]
    U --> W[ENTREGUE]
    U2 --> W
    S -. admin cancela .-> X
    W --> Fim((Fim))
    X --> Fim
```

## 5. Diagrama de estados do pedido

```mermaid
stateDiagram-v2
    [*] --> RECEBIDO: criar_pedido
    RECEBIDO --> EM_PREPARO: admin avança [pagamento liberado – RN08]
    RECEBIDO --> CANCELADO: cliente ou admin
    EM_PREPARO --> SAIU_PARA_ENTREGA: admin [tipo = ENTREGA]
    EM_PREPARO --> PRONTO_RETIRADA: admin [tipo = RETIRADA]
    EM_PREPARO --> CANCELADO: somente admin
    SAIU_PARA_ENTREGA --> ENTREGUE: admin
    PRONTO_RETIRADA --> ENTREGUE: admin
    SAIU_PARA_ENTREGA --> CANCELADO: somente admin
    PRONTO_RETIRADA --> CANCELADO: somente admin
    ENTREGUE --> [*]
    CANCELADO --> [*]
```

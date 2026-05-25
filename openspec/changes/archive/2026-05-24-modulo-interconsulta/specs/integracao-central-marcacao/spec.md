## ADDED Requirements

### Requirement: Mensageria Assíncrona e Retry
O sistema MUST garantir que todos os pedidos classificados pelo Motor de Regras sejam publicados em um Message Broker para entrega assíncrona à API da Central de Marcação do AGHU, implementando políticas de fallback/retry.

#### Scenario: Serviço da Central Indisponível
- **WHEN** o worker tentar despachar o pedido para a Central do AGHU e receber HTTP 503 Service Unavailable
- **THEN** o worker re-enfileira a tarefa automaticamente usando lógica de retry (exponencial backoff) e registra o evento na trilha de auditoria

#### Scenario: Entrega Bem Sucedida
- **WHEN** a integração com a Central de Marcação retornar HTTP 200 OK
- **THEN** o sistema atualiza o status do pedido localmente (via provider e SQL nativo) para "AGENDADO"

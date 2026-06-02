## Context

A Central de Marcação digital do AGHU recebe pedidos assincronamente através de mensageria local. Em casos de falhas de comunicação com a API externa (HTTP 503/500), as mensagens entram em estado de erro após tentativas automáticas (backoff exponencial). Além disso, a fila digital ordenada por prioridade (motor de regras) precisa ser monitorada visualmente por um operador da Central para efetivar os agendamentos manuais (caso necessário). O sistema atual expõe dados no backend, mas carece de uma interface unificada de regulação e suporte para re-envio/atualização manual.

## Goals / Non-Goals

**Goals:**
* Desenvolver uma interface administrativa reativa `/central-marcacao` para operadores reguladores.
* Implementar o endpoint `PATCH /api/interconsultas/{pedido_id}/status` no backend para permitir a regulação manual e atualização pelo worker.
* Implementar o endpoint `POST /api/interconsultas/{pedido_id}/retry` no backend para forçar o re-enfileiramento de pedidos com falha.
* Seguir estritamente o fluxo de dados em camadas: SQL ➔ Resource ➔ Provider ➔ Controller ➔ Router.
* Descriptografar o CNS de forma segura apenas sob demanda para operadores autorizados.
* Implementar trilha de auditoria (audit log) detalhada para acessos à visualização do CNS.
* Implementar a separação entre pacientes agendados e não agendados em filas distintas.

**Non-Goals:**
* Não será agendada assim que o médico solicitar (A central tem que marcar como agendado manualmente).
* Não será alterado o esquema de banco de dados principal (nenhuma migração de tabela nova é requerida).
* Não será permitida a exclusão física de registros (somente Soft Delete existente).
* Não haverá integração automática com outros brokers externos que não o Message Broker simulado atualmente.

## Decisions

### 1. Extensão do Provedor de Interconsulta Existente
* **Escolha:** Adicionar as novas operações diretamente em `InterconsultaProviderInterface` e estender suas implementações (`Postgres` e `Mock`).
* **Alternativa considerada:** Criar um provedor separado `CentralMarcacaoProvider`.
* **Razão:** Como as operações são sobre a mesma entidade/tabela de `interconsulta_pedidos`, manter no mesmo provedor reduz o acoplamento e reusa a lógica de conexão e decodificação/criptografia já estabelecida de forma limpa.

### 2. SQL Nativo para Atualização de Status
* **Escolha:** Criar um arquivo SQL isolado `atualizar_status_pedido.sql` no diretório `src/providers/sql/interconsulta/` para a atualização do status, contendo placeholders compatíveis com `sql_helper.py`.
* **Alternativa considerada:** Usar ORM Update do SQLAlchemy.
* **Razão:** O projeto adota a convenção de SQLs nativos na camada de dados (`SQL ➔ Resource ➔ Provider`) para consistência arquitetural com outros módulos (AIH, BPA).
* **SQL Template (atualizar_status_pedido.sql):**
  ```sql
  UPDATE interconsulta_pedidos
  SET status = :status, atualizado_em = CURRENT_TIMESTAMP
  WHERE id = :id AND deleted_at IS NULL
  RETURNING id, status, atualizado_em;
  ```

### 3. Trilha de Auditoria no Nível do Controller
* **Escolha:** Toda vez que a Central de Marcação listar os pedidos com dados decifrados, o controlador deve gravar um evento de auditoria no log do sistema especificando o ID do usuário que leu, o timestamp e o recurso acessado.
* **Alternativa considerada:** Registrar logs de auditoria no banco.
* **Razão:** O uso de logs estruturados de auditoria no backend atende aos requisitos iniciais da LGPD com performance adequada para o MVP, evitando escritas concorrentes desnecessárias no banco local em operações de leitura.

## Risks / Trade-offs

* **[Risco] Vazamento de Dados Sensíveis (CNS)** ➔ **Mitigação:** O CNS descriptografado só é retornado se o usuário possuir a claims de login válida e pertencer a um grupo autorizado (no caso de mock, `GLO-SEC-HCPE-SETISD` ou admin). O frontend não salva esse valor localmente além do estado reativo temporário da tabela.
* **[Risco] Concorrência em Atualizações de Status** ➔ **Mitigação:** A atualização manual verifica se o registro não está marcado como deletado (`deleted_at IS NULL`) antes de realizar o update.

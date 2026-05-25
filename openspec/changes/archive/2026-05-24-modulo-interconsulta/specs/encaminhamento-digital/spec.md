## ADDED Requirements

### Requirement: Registro de Interconsulta
O sistema MUST permitir que um médico solicite uma interconsulta selecionando sintomas de um catálogo pré-definido e garanta a persistência imutável dos dados (uso de Soft Delete `deleted_at`). Campos confidenciais MUST ser armazenados com criptografia AES-256 no banco de dados local.

#### Scenario: Submissão válida
- **WHEN** um médico envia um formulário preenchido com CNS do paciente, especialidade e array de sintomas
- **THEN** o sistema salva o pedido na base de dados (criptografando dados sensíveis de identificação via AES-256) e retorna status 201 Created

#### Scenario: Proteção contra Hard Delete
- **WHEN** o sistema precisa excluir ou inativar um registro de interconsulta
- **THEN** a operação MUST modificar a coluna `deleted_at` com a data atual (Soft Delete), preservando os dados físicos para auditoria

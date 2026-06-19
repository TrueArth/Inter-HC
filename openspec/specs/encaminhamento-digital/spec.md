# encaminhamento-digital Specification

## Purpose
TBD - created by archiving change modulo-interconsulta. Update Purpose after archive.
## Requirements
### Requirement: Registro de Interconsulta
O sistema MUST permitir que um médico solicite uma interconsulta selecionando sintomas de um catálogo pré-definido e garanta a persistência imutável dos dados (uso de Soft Delete `deleted_at`). Campos confidenciais MUST ser armazenados com criptografia AES-256 no banco de dados local.

#### Scenario: Submissão válida
- **WHEN** um médico envia um formulário preenchido com CNS do paciente, especialidade e array de sintomas
- **THEN** o sistema salva o pedido na base de dados (criptografando dados sensíveis de identificação via AES-256) e retorna status 201 Created

#### Scenario: Proteção contra Hard Delete
- **WHEN** o sistema precisa excluir ou inativar um registro de interconsulta
- **THEN** a operação MUST modificar a coluna `deleted_at` com a data atual (Soft Delete), preservando os dados físicos para auditoria

### Requirement: Restrição de Lista de Pedidos Ativos
O sistema MUST restringir a exibição da lista de pacientes e pedidos ativos na seção de solicitações de interconsulta, de forma que o médico solicitante não tenha visibilidade da fila regulatória geral.

#### Scenario: Acesso Médico à Solicitação de Interconsulta
- **WHEN** o médico acessar a rota `/interconsultas` para realizar uma nova solicitação
- **THEN** o sistema exibe apenas o formulário de submissão de nova interconsulta e MUST omitir ou remover qualquer card ou tabela contendo a lista de pedidos ativos ou dados de outros pacientes regulados.


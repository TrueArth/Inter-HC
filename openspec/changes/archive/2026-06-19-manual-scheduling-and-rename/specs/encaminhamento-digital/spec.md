## MODIFIED Requirements

### Requirement: Registro de Interconsulta
O sistema MUST permitir que um médico solicite uma interconsulta selecionando sintomas de um catálogo pré-definido e garanta a persistência imutável dos dados (uso de Soft Delete `deleted_at`). Campos confidenciais MUST ser armazenados com criptografia AES-256 no banco de dados local. Os novos pedidos criados pelo médico MUST ter status inicial 'PENDENTE' e não devem ser integrados/agendados automaticamente de forma assíncrona.

#### Scenario: Submissão válida
- **WHEN** um médico envia um formulário preenchido com CNS do paciente, especialidade e array de sintomas
- **THEN** o sistema salva o pedido na base de dados (criptografando dados sensíveis de identificação via AES-256) com status inicial 'PENDENTE', não realiza disparo automático de agendamento e retorna status 201 Created

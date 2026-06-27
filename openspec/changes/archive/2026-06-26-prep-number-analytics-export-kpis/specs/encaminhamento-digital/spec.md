## MODIFIED Requirements

### Requirement: Registro de Interconsulta
O sistema MUST permitir que um médico solicite uma interconsulta selecionando sintomas de um catálogo pré-definido e garanta a persistência imutável dos dados (uso de Soft Delete `deleted_at`). Campos confidenciais MUST ser armazenados com criptografia AES-256 no banco de dados local. Os novos pedidos criados pelo médico MUST ter status inicial 'PENDENTE'.
O número do CNS não será mais utilizado. Em seu lugar, o médico MUST informar o número do PREP (Prontuário Eletrônico do Paciente), que MUST conter entre 7 e 8 dígitos numéricos válidos.

#### Scenario: Submissão válida com número PREP
- **WHEN** um médico envia um formulário preenchido com o número do PREP do paciente contendo entre 7 e 8 dígitos numéricos, especialidade e array de sintomas
- **THEN** o sistema salva o pedido na base de dados (criptografando dados sensíveis de identificação via AES-256) com status inicial 'PENDENTE' e retorna status 201 Created

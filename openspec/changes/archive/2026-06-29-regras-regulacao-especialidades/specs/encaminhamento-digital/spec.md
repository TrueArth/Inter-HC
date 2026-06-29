## MODIFIED Requirements

### Requirement: Registro de Interconsulta
O sistema MUST permitir que um médico solicite uma interconsulta selecionando sintomas de um catálogo pré-definido e garanta a persistência imutável dos dados (uso de Soft Delete `deleted_at`). Campos confidenciais MUST ser armazenados com criptografia AES-256 no banco de dados local. Se o pedido for de gravidade VERMELHA ou AMARELA, ele MUST ter status inicial 'PENDENTE' e não deve ser integrado automaticamente de forma assíncrona. Se o pedido for de gravidade VERDE, ele MUST ter status 'ERRO' (encaminhamento falho) com o motivo `"Não é papel do HC"`.

#### Scenario: Submissão de gravidade Amarela/Vermelha
- **WHEN** um médico envia um formulário com o PREP do paciente (7 a 8 dígitos), especialidade e sintomas que resultem em gravidade Amarela ou Vermelha
- **THEN** o sistema salva o pedido na base de dados (criptografando dados sensíveis de identificação via AES-256) com status inicial 'PENDENTE', não realiza disparo de agendamento automático, retorna status 201 Created, e informa ao médico que a interconsulta foi registrada com sucesso (ocultando o nível de gravidade).

#### Scenario: Submissão de gravidade Verde
- **WHEN** um médico envia um formulário com sintomas que resultem in gravidade Verde
- **THEN** o sistema salva o pedido na base de dados com status 'ERRO', retorna status 201 Created, e informa ao médico que a interconsulta não foi marcada pelo motivo de não ser papel do HC (ocultando a gravidade).

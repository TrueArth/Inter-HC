# encaminhamento-digital Specification

## Purpose
TBD - created by archiving change modulo-interconsulta. Update Purpose after archive.
## Requirements
### Requirement: Registro de Interconsulta
O sistema MUST permitir que um médico solicite uma interconsulta selecionando sintomas de um catálogo pré-definido e garanta a persistência imutável dos dados (uso de Soft Delete `deleted_at`). Campos confidenciais MUST ser armazenados com criptografia AES-256 no banco de dados local. Se o pedido for de gravidade VERMELHA ou AMARELA, ele MUST ter status inicial 'PENDENTE' e não deve ser integrado automaticamente de forma assíncrona. Se o pedido for de gravidade VERDE, ele MUST ter status 'ERRO' (encaminhamento falho) com o motivo `"Não é papel do HC"`.

#### Scenario: Submissão de gravidade Amarela/Vermelha
- **WHEN** um médico envia um formulário com o PREP do paciente (7 a 8 dígitos), especialidade e sintomas que resultem in gravidade Amarela ou Vermelha
- **THEN** o sistema salva o pedido na base de dados (criptografando dados sensíveis de identificação via AES-256) com status inicial 'PENDENTE', não realiza disparo de agendamento automático, retorna status 201 Created, e informa ao médico que a interconsulta foi registrada com sucesso (ocultando o nível de gravidade).

#### Scenario: Submissão de gravidade Verde
- **WHEN** um médico envia um formulário com sintomas que resultem in gravidade Verde
- **THEN** o sistema salva o pedido na base de dados com status 'ERRO', retorna status 201 Created, e informa ao médico que a interconsulta não foi marcada pelo motivo de não ser papel do HC (ocultando a gravidade).

#### Scenario: Submissão com contato opcional do paciente
- **WHEN** um médico preenche o formulário de interconsulta e opcionalmente adiciona o número de contato do paciente no formato `(dd) xxxxx-xxxx` ou `(dd) xxxx-xxxx`
- **THEN** o sistema aceita a solicitação e persiste o contato encriptado via AES-256 no banco de dados local, retornando o registro criado com sucesso.

#### Scenario: Desfazer Envio de Solicitação
- **WHEN** o médico solicita uma nova interconsulta e clica em desfazer nos primeiros 30 segundos
- **THEN** o sistema cancela o envio e o formulário é restaurado ao seu estado anterior, sem persistir nenhuma informação no banco de dados local.

### Requirement: Restrição de Lista de Pedidos Ativos
O sistema MUST restringir a exibição da lista de pacientes e pedidos ativos na seção de solicitações de interconsulta, de forma que o médico solicitante não tenha visibilidade da fila regulatória geral.

#### Scenario: Acesso Médico à Solicitação de Interconsulta
- **WHEN** o médico acessar a rota `/interconsultas` para realizar uma nova solicitação
- **THEN** o sistema exibe apenas o formulário de submissão de nova interconsulta e MUST omitir ou remover qualquer card ou tabela contendo a lista de pedidos ativos ou dados de outros pacientes regulados.

### Requirement: Seleção Exata de Especialidade e Autocompletar de Sintomas
O sistema MUST apresentar uma lista suspensa (dropdown) com especialidades clínicas específicas para seleção e um campo de pesquisa reativo (autocomplete) para buscar e selecionar sintomas gerais.

#### Scenario: Preenchimento do Formulário pelo Médico
- **WHEN** o médico acessar a interface de criação de interconsulta
- **THEN** o sistema exibe uma lista suspensa para a seleção exata da especialidade e um campo de entrada de texto com autocompletar que exibe sintomas semelhantes à digitação, adicionando os sintomas escolhidos como tags associadas ao formulário.

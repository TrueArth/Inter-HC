# encaminhamento-digital Specification

## Purpose
TBD - created by archiving change modulo-interconsulta. Update Purpose after archive.
## Requirements
### Requirement: Registro de Interconsulta
O sistema MUST permitir que um médico solicite uma interconsulta selecionando sintomas de um catálogo pré-definido e garanta a persistência imutável dos dados (uso de Soft Delete `deleted_at`). Campos confidenciais MUST ser armazenados com criptografia AES-256 no banco de dados local. Os novos pedidos criados pelo médico MUST ter status inicial 'PENDENTE' e não devem ser integrados/agendados automaticamente de forma assíncrona.

#### Scenario: Submissão válida
- **WHEN** um médico envia um formulário preenchido com CNS do paciente, especialidade e array de sintomas
- **THEN** o sistema salva o pedido na base de dados (criptografando dados sensíveis de identificação via AES-256) com status inicial 'PENDENTE', não realiza disparo automático de agendamento e retorna status 201 Created

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


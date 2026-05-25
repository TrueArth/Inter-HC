## ADDED Requirements

### Requirement: Portal Web MVP de Solicitação de Interconsulta
O portal Vue MUST expor a rota autenticada `/interconsultas` com formulário que permita ao médico informar CNS (15 dígitos), código numérico de especialidade e seleção de ao menos um sintoma de um catálogo estático pré-definido (IDs alinhados ao motor de regras do backend), submetendo via `POST /api/interconsultas/` com token JWT.

#### Scenario: Acesso autenticado à rota
- **WHEN** um usuário autenticado navega para `/interconsultas`
- **THEN** o sistema exibe a página de interconsultas com formulário de nova solicitação e área de listagem de pedidos

#### Scenario: Bloqueio sem autenticação
- **WHEN** um usuário não autenticado tenta acessar `/interconsultas`
- **THEN** o router redireciona para a tela de login

#### Scenario: Validação de formulário no cliente
- **WHEN** o médico tenta enviar com CNS inválido, especialidade menor que 1 ou nenhum sintoma selecionado
- **THEN** o sistema impede a chamada à API e informa o erro ao usuário sem submeter o pedido

#### Scenario: Submissão bem-sucedida
- **WHEN** o médico preenche CNS válido, especialidade e sintomas do catálogo e confirma o envio
- **THEN** o frontend chama `POST /api/interconsultas/`, exibe confirmação com a gravidade retornada pelo servidor e atualiza a listagem de pedidos

### Requirement: Listagem de Pedidos Ativos na Interface
A tela `/interconsultas` MUST exibir os pedidos retornados por `GET /api/interconsultas/`, mostrando identificador, especialidade, gravidade (com distinção visual por cor), status e data de criação, na ordem definida pelo backend.

#### Scenario: Carregamento inicial da lista
- **WHEN** a página `/interconsultas` é montada
- **THEN** o frontend solicita `GET /api/interconsultas/` e renderiza os pedidos ativos na tabela

#### Scenario: Atualização após nova solicitação
- **WHEN** um novo pedido é criado com sucesso via formulário
- **THEN** a tabela de pedidos é recarregada e exibe o novo registro incluindo a gravidade calculada pelo servidor

### Requirement: Mascaramento de CNS na Exibição
A interface MUST NOT exibir o CNS completo na tabela de listagem; MUST mostrar apenas representação mascarada (por exemplo, últimos 4 dígitos precedidos de caracteres de ocultação).

#### Scenario: CNS mascarado na tabela
- **WHEN** a listagem de pedidos é renderizada
- **THEN** a coluna de identificação do paciente exibe o CNS parcialmente mascarado e não o valor integral em texto claro

# visualizacao-central-marcacao Specification

## Purpose
TBD - created by archiving change visualizacao-central-marcacao. Update Purpose after archive.
## Requirements
### Requirement: Painel de Regulação Centralizado
O sistema MUST disponibilizar um painel digital centralizado (Dashboard de Regulação) que exiba a fila de solicitações ativas ordenada por gravidade (VERMELHO ➔ AMARELO ➔ VERDE) e depois por data de criação. A interface e a API MUST retornar e exibir de forma legível os valores numéricos de pontuação (prioridade) e dias em fila para cada solicitação.

#### Scenario: Visualização da Fila Priorizada
- **WHEN** o operador da Central de Marcação acessar a rota `/central-marcacao`
- **THEN** o sistema exibe os pedidos ativos no topo os de gravidade 'VERMELHO', seguidos por 'AMARELO' e 'VERDE', com dados do paciente decifrados (CNS completo), médico solicitante, data, e os valores numéricos corretos de pontuação (score) e dias na fila (sem estarem vazios ou omitidos).

### Requirement: Detalhamento de Sintomas Justificadores
O painel MUST permitir visualizar a lista completa de sintomas padronizados que justificaram a gravidade clínica de uma solicitação de interconsulta.

#### Scenario: Exibição dos Detalhes Clinicos
- **WHEN** o operador selecionar um pedido na fila do painel
- **THEN** o sistema exibe um modal ou aba detalhada com os sintomas e dados clínicos associados àquela solicitação.

### Requirement: Alteração Manual de Status
O sistema MUST permitir que o operador da Central altere manualmente o status de uma interconsulta para 'AGENDADO' ou 'ERRO' diretamente pela interface.

#### Scenario: Atualizar Status Manualmente
- **WHEN** o operador marcar um pedido específico como concluído/agendado no painel
- **THEN** o sistema envia uma requisição de atualização, persiste o status 'AGENDADO' na base de dados (via SQL nativo e provider) e atualiza a interface visual.

### Requirement: Identidade Visual InterHC
O sistema MUST expor a denominação "InterHC" em todas as áreas principais de branding no frontend.

#### Scenario: Visualização do Nome do Aplicativo
- **WHEN** qualquer usuário acessar o painel do frontend
- **THEN** o sistema exibe "InterHC" no logotipo e título da barra lateral, e na tag title da página no navegador.

### Requirement: Exibição Amigável de Especialidades
O sistema MUST resolver o ID numérico da especialidade e exibir o nome por extenso correspondente em todas as views de listagem e detalhamento da Central de Marcação.

#### Scenario: Visualização do Nome da Especialidade na Fila
- **WHEN** o operador acessar a fila digital na Central de Marcação
- **THEN** o sistema exibe o nome legível por extenso da especialidade (ex: "Cardiologia") nas células da tabela e no drawer de detalhes em vez de apenas o ID numérico.


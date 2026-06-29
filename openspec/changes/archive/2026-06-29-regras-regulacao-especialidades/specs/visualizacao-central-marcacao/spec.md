## MODIFIED Requirements

### Requirement: Painel de Regulação Centralizado
O sistema MUST disponibilizar um painel digital centralizado (Dashboard de Regulação) que exiba a fila de solicitações ativas ordenada por gravidade (VERMELHO ➔ AMARELO) e depois por data de criação. Pedidos com gravidade VERDE não devem ser exibidos ou regulados na Central de Marcação. A interface MUST exibir apenas o número do PREP decifrado do paciente, omitindo o nome do paciente, ID numérico do pedido ou ordem de criação. A interface e a API MUST retornar e exibir de forma legível os valores numéricos de pontuação (prioridade) e dias em fila para cada solicitação.

#### Scenario: Visualização da Fila Priorizada
- **WHEN** o operador da Central de Marcação acessar a rota `/central-marcacao`
- **THEN** o sistema exibe os pedidos ativos no topo os de gravidade 'VERMELHO', seguidos por 'AMARELO', ocultando pedidos de gravidade 'VERDE'. O sistema exibe apenas o PREP completo do paciente (dados de nome, IDs do banco e ordem de criação do pedido MUST ser omitidos para evitar erros e manter privacidade), médico solicitante, data, e os valores numéricos corretos de pontuação (score) e dias na fila (sem estarem vazios ou omitidos).

### Requirement: Detalhamento de Sintomas Justificadores
O painel MUST permitir visualizar a lista completa de sintomas padronizados que justificaram a gravidade clínica de uma solicitação de interconsulta.

#### Scenario: Exibição dos Detalhes Clinicos
- **WHEN** o operador selecionar um pedido na fila do painel
- **THEN** o sistema exibe um modal ou aba detalhada com os sintomas e dados clínicos associados àquela solicitação, sem expor o nome do paciente.

### Requirement: Alteração Manual de Status
O sistema MUST permitir que o operador da Central altere manualmente o status de uma interconsulta para 'AGENDADO' ou 'ERRO' diretamente pela interface. Pedidos de gravidade VERDE não podem aparecer na fila nem para tentativas de re-envio.

#### Scenario: Atualizar Status Manualmente
- **WHEN** o operador marcar um pedido específico como concluído/agendado no painel
- **THEN** o sistema envia uma requisição de atualização, persiste o status 'AGENDADO' na base de dados (via SQL nativo e provider) e atualiza a interface visual.

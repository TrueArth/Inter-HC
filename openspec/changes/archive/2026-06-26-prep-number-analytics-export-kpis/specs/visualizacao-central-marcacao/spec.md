## MODIFIED Requirements

### Requirement: Painel de Regulação Centralizado
O sistema MUST disponibilizar um painel digital centralizado (Dashboard de Regulação) que exiba a fila de solicitações ativas ordenada por gravidade (VERMELHO ➔ AMARELO ➔ VERDE) e depois por data de criação. A interface e a API MUST retornar e exibir de forma legível os valores numéricos de pontuação (prioridade) e dias em fila para cada solicitação.

#### Scenario: Visualização da Fila Priorizada
- **WHEN** o operador da Central de Marcação acessar a rota `/central-marcacao`
- **THEN** o sistema exibe os pedidos ativos no topo os de gravidade 'VERMELHO', seguidos por 'AMARELO' e 'VERDE', com dados do paciente decifrados contendo o número do PREP completo (no lugar do CNS), médico solicitante, data, e os valores numéricos corretos de pontuação (score) e dias na fila.

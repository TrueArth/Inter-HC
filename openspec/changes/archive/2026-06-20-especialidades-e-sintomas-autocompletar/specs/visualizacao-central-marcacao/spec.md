## ADDED Requirements

### Requirement: Exibição Amigável de Especialidades
O sistema MUST resolver o ID numérico da especialidade e exibir o nome por extenso correspondente em todas as views de listagem e detalhamento da Central de Marcação.

#### Scenario: Visualização do Nome da Especialidade na Fila
- **WHEN** o operador acessar a fila digital na Central de Marcação
- **THEN** o sistema exibe o nome legível por extenso da especialidade (ex: "Cardiologia") nas células da tabela e no drawer de detalhes em vez de apenas o ID numérico.

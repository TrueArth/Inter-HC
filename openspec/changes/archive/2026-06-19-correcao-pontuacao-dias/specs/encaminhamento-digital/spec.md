## ADDED Requirements

### Requirement: Restrição de Lista de Pedidos Ativos
O sistema MUST restringir a exibição da lista de pacientes e pedidos ativos na seção de solicitações de interconsulta, de forma que o médico solicitante não tenha visibilidade da fila regulatória geral.

#### Scenario: Acesso Médico à Solicitação de Interconsulta
- **WHEN** o médico acessar a rota `/interconsultas` para realizar uma nova solicitação
- **THEN** o sistema exibe apenas o formulário de submissão de nova interconsulta e MUST omitir ou remover qualquer card ou tabela contendo a lista de pedidos ativos ou dados de outros pacientes regulados.

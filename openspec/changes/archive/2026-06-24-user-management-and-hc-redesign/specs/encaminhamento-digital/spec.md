## MODIFIED Requirements

### Requirement: Restrição de Lista de Pedidos Ativos
O sistema MUST restringir o acesso à tela de solicitação de interconsulta `/interconsultas` a usuários com perfil 'medico' ou 'admin'. O sistema MUST também omitir qualquer lista ou tabela de pedidos ativos de outros pacientes para usuários médicos, garantindo que o médico solicitante não tenha visibilidade da fila regulatória geral.

#### Scenario: Acesso Médico à Solicitação de Interconsulta
- **WHEN** o médico acessar a rota `/interconsultas` para realizar uma nova solicitação
- **THEN** o sistema exibe apenas o formulário de submissão de nova interconsulta e MUST omitir ou remover qualquer card ou tabela contendo a lista de pedidos ativos ou dados de outros pacientes regulados.

#### Scenario: Bloqueio de Acesso para Reguladores
- **WHEN** um usuário com perfil 'regulador' tenta acessar a rota `/interconsultas`
- **THEN** o sistema bloqueia o acesso, redireciona o usuário e impede o consumo dos endpoints da API correspondentes (retornando 403 Forbidden)

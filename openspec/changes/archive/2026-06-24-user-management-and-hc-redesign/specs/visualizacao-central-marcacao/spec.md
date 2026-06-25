## MODIFIED Requirements

### Requirement: Painel de Regulação Centralizado
O sistema MUST disponibilizar um painel digital centralizado (Dashboard de Regulação) que exiba a fila de solicitações ativas ordenada por gravidade (VERMELHO ➔ AMARELO ➔ VERDE) e depois por data de criação. A interface e a API MUST retornar e exibir de forma legível os valores numéricos de pontuação (prioridade) e dias em fila para cada solicitação. O acesso a esse painel MUST ser exclusivo para usuários com perfil 'regulador' ou 'admin'. Quando uma interconsulta for agendada, o sistema MUST registrar e exibir a identificação (username) do marcador responsável pelo agendamento.

#### Scenario: Visualização da Fila Priorizada
- **WHEN** o operador da Central de Marcação (com perfil 'regulador' ou 'admin') acessar a rota `/central-marcacao`
- **THEN** o sistema exibe os pedidos ativos no topo os de gravidade 'VERMELHO', seguidos por 'AMARELO' e 'VERDE', com dados do paciente decifrados (CNS completo), médico solicitante, data, e os valores numéricos corretos de score e dias na fila

#### Scenario: Visualização do Identificador do Marcador no Agendamento
- **WHEN** o operador visualizar uma consulta com status 'AGENDADO' na interface
- **THEN** o sistema exibe de forma clara na descrição/detalhes o identificador do marcador (username do regulador) que marcou a consulta

#### Scenario: Bloqueio de Acesso para Médicos
- **WHEN** um usuário com perfil 'medico' tenta acessar a rota `/central-marcacao`
- **THEN** o sistema bloqueia o acesso, redireciona o usuário e impede o consumo dos endpoints da API correspondentes (retornando 403 Forbidden)

### Requirement: Identidade Visual InterHC
O sistema MUST expor a denominação "InterHC" em todas as áreas principais de branding no frontend, com um layout visual customizado baseado em tons de azul e alinhado à identidade visual do Hospital das Clínicas da UFPE (HC-UFPE).

#### Scenario: Visualização do Nome do Aplicativo e Identidade UFPE
- **WHEN** qualquer usuário acessar o painel do frontend
- **THEN** o sistema exibe "InterHC" no logotipo e título da barra lateral, na tag title da página, estilizado com a paleta de cores azuis do HC-UFPE e sem referências à aba "Exemplos" (que MUST ser removida)

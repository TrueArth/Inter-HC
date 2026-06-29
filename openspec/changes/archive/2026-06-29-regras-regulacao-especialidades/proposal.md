## Why

O fluxo regulatório do HCPE necessita de melhorias de usabilidade no filtro de especialidades na Central de Marcação e no gerenciamento de sintomas na Central de Administração, bem como correções no tratamento e privacidade de pacientes classificados com gravidade "VERDE". Os médicos não devem ter acesso ao nível de gravidade, e dados desnecessários de identificação (como nome ou ordem de criação do pedido) devem ser omitidos para evitar erros regulatórios e manter conformidade com LGPD.

## What Changes

* **Ajuste do Filtro de Especialidades:** Em Central de Marcação e Admin (Sintomas), o filtro por especialidade não oculta as demais caixas ao ser selecionado, e pode ser desmarcado clicando no botão ativo novamente (revertendo ao estado global).
* **Bloqueio de Pacientes VERDE:** Pacientes classificados como gravidade VERDE são salvos com status ERRO e o motivo "Não é papel do HC". Eles não são enfileirados e ficam completamente ocultos na Central de Marcação.
* **Omissão de Dados do Paciente:** Ocultação de paciente_nome, ID do banco (#numero) e ordem de criação nas telas da Central de Marcação, exibindo apenas o PREP do paciente.
* **Ocultação da Gravidade para Médicos:** O toast de sucesso da criação do pedido não exibe a gravidade calculada, informando apenas se foi registrado ou se não foi marcado (no caso de VERDE) devido ao motivo "Não é papel do HC".

## Capabilities

### Modified Capabilities
- `visualizacao-central-marcacao`: Remoção de ID, nome do paciente, ocultação de gravidade VERDE e comportamento aprimorado do filtro.
- `encaminhamento-digital`: Alteração no fluxo de gravidade VERDE (não enfileira, status ERRO com motivo) e ocultação do nível de risco para médicos.
- `admin-statistics`: Ajuste na aba de sintomas para remover o botão "Todas" e adicionar comportamento de alternar filtro.

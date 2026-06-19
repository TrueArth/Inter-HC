## Why

Atualmente, ao submeter uma nova solicitação de interconsulta, o sistema altera seu status automaticamente para `ENFILEIRADO` e dispara de forma assíncrona o envio e agendamento automático na API do AGHU legado. A equipe clínica solicita que não ocorra agendamento imediato/automático na submissão do médico; todas as interconsultas devem iniciar como pendentes e ser reguladas/agendadas exclusivamente de forma manual pela equipe da Central de Marcação. Adicionalmente, para alinhar a identidade visual do portal ao padrão corporativo, a aplicação deve ser renomeada de "My App" para "InterHC".

## What Changes

- **Fluxo de Agendamento Manual**:
  - Modificar a criação de interconsultas no backend para inicializar o status do pedido como `PENDENTE` em vez de `ENFILEIRADO`.
  - Remover o disparo automático da tarefa assíncrona (`enviar_para_central_aghu`) no Message Broker durante a criação do pedido.
- **Renomeação do Projeto**:
  - Alterar o título da aplicação de "My App" para "InterHC" na barra de navegação superior móvel e na barra lateral do painel do frontend (`DefaultLayout.vue`).
  - Alterar a tag `<title>` em `index.html` para "InterHC".

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `encaminhamento-digital`: O processo de criação de interconsulta passa a gerar um pedido com status `PENDENTE` e sem integração automática, aguardando regulação.
- `visualizacao-central-marcacao`: Garante que a regulação seja estritamente manual pela central a partir dos pedidos em estado `PENDENTE`.

## Impact

### Fluxo de Dados em Camadas Afetado:
1. **Controller**: `InterconsultaController.solicitar_interconsulta` define status `PENDENTE` e não executa o dispatch no broker.
2. **FrontendLayout**: A navegação lateral e cabeçalho exibem "InterHC".
3. **Frontend HTML**: O título do navegador exibe "InterHC".

### Arquivos Modificados:
- [MODIFY] [interconsulta_controller.py](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/src/controllers/interconsulta_controller.py)
- [MODIFY] [DefaultLayout.vue](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/frontend/src/layouts/DefaultLayout.vue)
- [MODIFY] [index.html](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/frontend/index.html)

### Impacto nas Diretrizes LGPD e Trilhas de Auditoria:
- **LGPD**: Nenhuma nova informação confidencial é exposta. O controle de acesso a dados regulatórios é mantido na Central de Marcação.
- **Auditoria**: A trilha de auditoria continuará registrando acessos à fila e ações manuais de alteração de status realizadas pelo operador.

## Why

1. **Privacidade e LGPD:** A aba de pacientes para o perfil de administrador permitia listar prontuários e nomes de pacientes, expondo dados pessoais sensíveis sem necessidade estrita para fins regulatórios e administrativos. Removê-la reduz a superfície de risco e restringe o acesso direto a prontuários.
2. **Prevenção de Erros Clínicos:** Médicos e reguladores trabalham em ambientes hospitalares de alta pressão. Erros ao solicitar ou agendar interconsultas acontecem frequentemente. Disponibilizar um tempo de 30 segundos para desfazer qualquer ação de criação, agendamento ou reprocessamento previne envios incorretos antes de atingirem o banco de dados principal e a integração com o AGHU.

## What Changes

* **Remoção da Aba Pacientes:** Exclusão da rota, links de sidebar e dashboard card para o cadastro de pacientes no perfil de administrador.
* **Mecanismo de Desfazer de 30s (Client-side Undo):** Implementação de um banner de desfazer no frontend Vue 3. Toda ação de escrita (solicitação de interconsulta pelo médico, agendamento de consulta pelo regulador e re-envio manual) é retida localmente por 30 segundos, permitindo rollback imediato.

## Capabilities

### Deleted Capabilities
- `admin-pacientes-management`: Capacidade de acessar e ler prontuários diretamente da lista de pacientes.

### Modified Capabilities
- `encaminhamento-digital`: Inclui a capacidade de desfazer o envio da solicitação nos primeiros 30 segundos.
- `visualizacao-central-marcacao`: Inclui a capacidade de desfazer agendamentos e retentativas nos primeiros 30 segundos.

## Impact

### Fluxo de Dados em Camadas
Não há impacto em camadas de dados do backend, pois a retenção de 30 segundos é implementada de forma reativa no frontend (Pinia/Vue), atrasando o envio HTTP à API.

### Arquivos Afetados

* **[DELETE]**
  * `frontend/src/views/Pacientes.vue`
* **[MODIFY]**
  * `frontend/src/router/index.ts`
  * `frontend/src/layouts/DefaultLayout.vue`
  * `frontend/src/views/Home.vue`
  * `frontend/src/views/Interconsultas.vue`
  * `frontend/src/views/CentralMarcacao.vue`
  * `frontend/src/stores/interconsulta.ts`
  * `openspec/specs/encaminhamento-digital/spec.md`
  * `openspec/specs/visualizacao-central-marcacao/spec.md`

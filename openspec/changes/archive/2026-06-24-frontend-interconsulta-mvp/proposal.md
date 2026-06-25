## Why

O backend do módulo de interconsulta já expõe `POST` e `GET` em `/api/interconsultas` com motor de regras, JWT e persistência LGPD, mas não existe interface no portal Vue. Médicos continuam sem canal digital para solicitar encaminhamentos, deixando a capability `encaminhamento-digital` incompleta do ponto de vista do usuário. Este change entrega o MVP da rota `/interconsultas` para fechar o fluxo ponta a ponta (formulário → API → listagem com gravidade).

## What Changes

* Nova rota autenticada `/interconsultas` no Vue Router com item no menu lateral.
* Tela única com formulário de solicitação (CNS, especialidade, sintomas via catálogo estático alinhado ao `RiskEngineService`) e tabela de pedidos ativos.
* Store Pinia `interconsulta` consumindo `POST /api/interconsultas/` e `GET /api/interconsultas/` via cliente `api.ts` existente (Bearer JWT).
* Validação client-side mínima (CNS 15 dígitos, especialidade ≥ 1, ao menos um sintoma).
* Exibição de gravidade retornada pelo servidor (badges VERMELHO/AMARELO/VERDE) e mascaramento parcial do CNS na listagem.
* **Fora de escopo neste MVP:** integração AGHU para paciente/especialidade dinâmica, preview de gravidade no client, cancelamento (`DELETE`) na UI, dashboard da Central de Marcação.

## Capabilities

### New Capabilities

_(nenhuma — requisitos de UI estendem capability existente)_

### Modified Capabilities

- `encaminhamento-digital`: Adicionar requisitos de interface web MVP (rota `/interconsultas`, formulário, listagem, catálogo estático de sintomas, mascaramento de CNS na exibição).

## Impact

* **Arquivos [NEW]:**
  * `frontend/src/stores/interconsulta.ts`
  * `frontend/src/views/Interconsultas.vue`
* **Arquivos [MODIFY]:**
  * `frontend/src/router/index.ts` (rota `/interconsultas`, `requiresAuth`)
  * `frontend/src/layouts/DefaultLayout.vue` (link de navegação)
* **APIs consumidas (sem alteração de contrato):** `POST /api/interconsultas/`, `GET /api/interconsultas/`
* **LGPD:** CNS mascarado na tabela (últimos 4 dígitos); valor completo apenas no payload de criação; sem armazenamento extra no front além do estado da sessão.
* **Backend:** Nenhuma mudança obrigatória; opcionalmente documentar que `medico_solicitante_crm` no body é sobrescrito pelo JWT no servidor.

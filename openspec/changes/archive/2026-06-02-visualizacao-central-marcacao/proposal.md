## Why

A equipe de regulação da Central de Marcação necessita de uma interface digital (Dashboard de Regulação) que apresente a fila de pedidos de interconsulta de forma integrada e priorizada de acordo com o nível de gravidade clínica (calculado pelo Motor de Regras). Sem isso, os operadores carecem de visibilidade das solicitações digitais para agendamento no AGHU, inviabilizando o processo regulatório otimizado e gerando gargalos operacionais.

## What Changes

* **Dashboard de Regulação (UI/UX Premium):** Criação de uma interface reativa no frontend Vue 3 (`/central-marcacao`) contendo a listagem dinâmica de pedidos ativos ordenados por gravidade clínica (Vermelho ➔ Amarelo ➔ Verde) e data de criação.
* **Detalhes do Pedido e Sintomas:** Opção de visualizar os detalhes de cada interconsulta, incluindo a lista de sintomas selecionados pelo médico solicitante para justificar a priorização.
* **Ações de Regulação:** Permissão para que o operador da Central atualize o status do pedido manualmente para `AGENDADO` (quando a marcação no AGHU legado for efetuada) ou dispare um retry manual (caso o envio automático via mensageria assíncrona falhe e o pedido fique em `ERRO`).
* **Trilhas de Auditoria (LGPD):** Descriptografia do CNS no backend e envio somente sob HTTPS para operadores autenticados, com log de auditoria registrando qual regulador visualizou quais dados de paciente.
* **Fluxo de Dados em Camadas:** Implementação estrita seguindo `SQL` ➔ `Resource` ➔ `Provider` ➔ `Controller` ➔ `Router`.

## Capabilities

### New Capabilities
- `visualizacao-central-marcacao`: Interface interativa e endpoints dedicados à equipe de regulação da Central de Marcação para visualização, monitoramento de filas prioritárias e controle de status de solicitações.

### Modified Capabilities
- `integracao-central-marcacao`: Extensão do escopo para permitir atualização de status no banco de dados e retry sob demanda via controle operacional do painel.

## Impact

* **Fluxo de Dados em Camadas (Fidelidade Arquitetural):**
  * `SQL`: Novo arquivo SQL nativo para alteração de status do pedido (`atualizar_status_pedido.sql`).
  * `Resource`: Utilização da sessão ativa do banco para execução das transações.
  * `Provider`: Extensão do `InterconsultaProviderInterface` com os métodos `atualizar_status_pedido(pedido_id, status)` e implementações correspondentes em Postgres e Mock providers.
  * `Controller`: Inclusão no `InterconsultaController` dos fluxos de negócio para alteração de status e retry de trabalhadores.
  * `Router`: Novas rotas `PATCH /api/interconsultas/{pedido_id}/status` e `POST /api/interconsultas/{pedido_id}/retry` no roteador `interconsulta.py`.

* **Arquivos Afetados (Visão Preliminar):**
  * [NEW] `src/providers/sql/interconsulta/atualizar_status_pedido.sql`
  * [NEW] `frontend/src/views/CentralMarcacao.vue`
  * [MODIFY] `src/providers/interfaces/interconsulta_provider_interface.py`
  * [MODIFY] `src/providers/implementations/interconsulta_postgres_provider.py`
  * [MODIFY] `src/providers/implementations/interconsulta_mock_provider.py`
  * [MODIFY] `src/controllers/interconsulta_controller.py`
  * [MODIFY] `src/routers/interconsulta.py`
  * [MODIFY] `frontend/src/router/index.ts` (Adição da rota com guardas de autenticação)
  * [MODIFY] `frontend/src/layouts/DefaultLayout.vue` (Link no menu lateral de navegação)

* **LGPD e Trilha de Auditoria:** 
  * A descriptografia do CNS é feita apenas em tempo de execução no backend. O CNS legível nunca é armazenado de forma persistente sem criptografia. 
  * Cada leitura ou exportação de dados do paciente para a Central gera um registro persistente na tabela de auditoria (quem acessou, quando e o ID do registro).
  * Manutenção estrita do Soft Delete (`deleted_at`) sem o uso de `DELETE` físico em tabelas de negócio.

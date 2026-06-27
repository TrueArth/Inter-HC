## Why

O número do CNS (Cartão Nacional de Saúde) com 15 dígitos está sendo descontinuado no fluxo regulatório do hospital. Deve-se adotar o número do PREP (Prontuário Eletrônico do Paciente), que varia de 7 a 8 dígitos numéricos. Além disso, a coordenação da Central de Regulação necessita de novos KPIs analíticos consolidados no painel de administração e de uma forma prática de exportar esses dados de regulação e solicitações para o Microsoft Excel para relatórios externos e auditorias adicionais.

## What Changes

* **Substituição de CNS por PREP:** Descontinuação do campo CNS na criação e exibição de interconsultas. Implementação de validação rígida de 7 a 8 dígitos numéricos para o PREP.
* **Novos KPIs no Dashboard:** Inclusão de estatísticas para:
  1. Total de interconsultas.
  2. Mapeamento de demanda de interconsultas por especialidade.
  3. Tempo médio de atendimento da marcação (tempo decorrido entre a criação do pedido e a marcação como AGENDADO).
  4. Ranking de especialidades com mais solicitações com status PENDENTE.
* **Exportação para Excel:** Endpoint no backend `/api/admin/statistics/export` que utiliza pandas e openpyxl para gerar uma planilha (.xlsx) com múltiplas abas: Visão Geral de KPIs, Demanda por Especialidade, Pendências por Especialidade, e a Lista de Solicitações Ativas. Um botão no frontend Vue (Aba Estatísticas) permite baixar o arquivo.

## Capabilities

### New Capabilities
- `analytics-export`: Capacidade de exportar em tempo real dados estatísticos e a fila regulatória decifrada em formato Excel (.xlsx) para usuários com papel 'admin'.

### Modified Capabilities
- `encaminhamento-digital`: Ajustado para validar e exigir o PREP (7-8 dígitos) do paciente ao invés de CNS (15 dígitos).
- `visualizacao-central-marcacao`: Ajustado para exibir o número do PREP do paciente no painel de regulação centralizado.
- `admin-statistics`: Enriquecido com novos KPIs analíticos (tempo médio de atendimento e pendências).

## Impact

### Fluxo de Dados em Camadas
Seguindo o fluxo regulamentado de camadas: `SQL ➔ Resource ➔ Provider ➔ Controller ➔ Router`
* **SQL:** Ajustes nas queries `inserir_pedido.sql` e `listar_pedidos.sql` em `src/providers/sql/interconsulta/` para referenciar a coluna `paciente_prep` no lugar de `paciente_cns`.
* **Resource:** Acesso ao banco de dados pelo Alembic para alterar o schema das tabelas.
* **Provider:** Mapeamento do atributo `paciente_prep` nas classes `InterconsultaPostgresProvider` e `InterconsultaMockProvider`.
* **Controller:** Ajuste da lógica de formatação de nomes em `InterconsultaController` buscando por `prep` (anteriormente `cns`) no arquivo `data/pacientes.csv`.
* **Router:** Exposição do novo endpoint de exportação de Excel no `src/routers/admin.py` sob `/api/admin/statistics/export` e adição dos novos campos no schema de retorno de estatísticas `/api/admin/statistics`.

### Arquivos Afetados

* **[NEW]**
  * `alembic/versions/eccfa4ee91c7_rename_cns_to_prep.py`
  * `openspec/changes/2026-06-26-prep-number-analytics-export-kpis/specs/analytics-dashboard/spec.md`
* **[MODIFY]**
  * `requirements.txt` / `pyproject.toml`
  * `src/models/interconsulta.py`
  * `src/schemas/interconsulta_schema.py`
  * `src/providers/sql/interconsulta/inserir_pedido.sql`
  * `src/providers/sql/interconsulta/listar_pedidos.sql`
  * `src/providers/implementations/interconsulta_postgres_provider.py`
  * `src/providers/implementations/interconsulta_mock_provider.py`
  * `src/controllers/interconsulta_controller.py`
  * `src/routers/admin.py`
  * `src/main.py`
  * `data/pacientes.csv`
  * `data/interconsultas.json`
  * `frontend/src/stores/interconsulta.ts`
  * `frontend/src/views/Interconsultas.vue`
  * `frontend/src/views/CentralMarcacao.vue`
  * `frontend/src/views/Admin.vue`
  * `openspec/specs/encaminhamento-digital/spec.md`
  * `openspec/specs/visualizacao-central-marcacao/spec.md`

### LGPD e Trilhas de Auditoria
* O número do PREP do paciente é considerado dado pessoal sensível sob a LGPD e continuará sendo encriptado via AES-256 no banco de dados local. Ele só será decifrado no momento de exibição na Central de Marcação (para reguladores) ou na geração do relatório de exportação em Excel (para administradores).
* O log de auditoria registrará quando o relatório em Excel for gerado e por qual administrador (`AUDITORIA: Usuario 'admin' exportou os dados analiticos para planilha Excel.`).

## 1. Backend Schema & Tests

- [x] 1.1 Modificar `src/schemas/interconsulta_schema.py` adicionando os campos `score_prioridade` (float) e `dias_na_fila` (int) como opcionais na classe `InterconsultaResponse`.
- [x] 1.2 Implementar testes unitários em `tests/` para verificar a correta serialização e retorno desses campos na rota `GET /api/interconsultas/`.

## 2. Frontend View Adjustments

- [x] 2.1 Modificar `frontend/src/views/CentralMarcacao.vue` para incluir as colunas "Pontuação" e "Tempo de Espera" na tabela principal de regulação.
- [x] 2.2 Atualizar `frontend/src/views/CentralMarcacao.vue` para mostrar a pontuação e o tempo de espera no drawer/painel de detalhes.
- [x] 2.3 Modificar `frontend/src/views/Interconsultas.vue` para remover a tabela e card de "Pedidos ativos" (lista de pacientes) e a lógica de recarga/carregamento relacionada.

## 1. Backend Implementation

- [x] 1.1 Atualizar `src/services/risk_engine_service.py` para aceitar `especialidade_id` na determinação de risco, expandir o catálogo interno de sintomas e definir as regras de promoção/override de gravidade.
- [x] 1.2 Modificar `src/controllers/interconsulta_controller.py` para passar o `especialidade_id` à chamada do motor de risco.
- [x] 1.3 Atualizar ou adicionar testes unitários para a classificação de risco condicional no backend.

## 2. Frontend Implementation

- [x] 2.1 Atualizar `frontend/src/stores/interconsulta.ts` adicionando a lista estática de especialidades (InterHC) e expandindo a lista `SINTOMAS_CATALOGO_MVP`.
- [x] 2.2 Modificar `frontend/src/views/Interconsultas.vue` substituindo a entrada numérica por uma lista suspensa (`<select>`) com as especialidades mapeadas.
- [x] 2.3 Modificar `frontend/src/views/Interconsultas.vue` implementando o campo de busca de sintomas por autocompletar reativo e exibição/remoção de tags.
- [x] 2.4 Modificar `frontend/src/views/CentralMarcacao.vue` (tabela e drawer de detalhes) para exibir o nome amigável por extenso das especialidades.

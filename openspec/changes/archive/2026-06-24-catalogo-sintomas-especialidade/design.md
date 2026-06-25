## Context

Atualmente, o painel do administrador (`Admin.vue`) exibe todos os sintomas carregados do banco na tabela de catálogo de sintomas. À medida que o sistema escala, a listagem de sintomas torna-se imensa.

## Decisions

### 1. Seleção no Topo por Abas (Estilo CentralMarcacao)

**Escolha:** Pílulas/botões horizontais com quebra de linha (`flex flex-wrap gap-2`).
**Rationale:** Segue o mesmo padrão visual adotado na Central de Marcação para seleção de filas por especialidade, promovendo consistência visual no sistema.

### 2. Filtro Combinado Reativo no Client

**Escolha:** Uso de propriedade computada `sintomasFiltrados` unificando o termo de busca `buscaSintoma` e o filtro de especialidade `especialidadeFiltro`.
**Rationale:** Executa a filtragem instantaneamente sem requisições adicionais à API, visto que o catálogo completo já é carregado ao entrar na aba.

### 3. Associação via Regras de Gravidade

**Escolha:** Identificar a associação do sintoma com a especialidade a partir do array de regras de gravidade.
**Rationale:** Como a tabela de sintomas não possui uma chave estrangeira direta para especialidade no banco, as regras customizadas atuam como mapeadores de pertinência.

## Risks / Trade-offs

* **Performance de Filtro no Client:** Filtrar 30+ sintomas no navegador é extremamente rápido. Caso o catálogo cresça para milhares de itens, uma paginação server-side com filtros via query parameters será recomendada.

## Context

Atualmente, `especialidade_id` é um inteiro preenchido manualmente na interface pelo médico. O motor de cálculo de risco (`RiskEngineService`) apenas considera IDs fixos de sintomas de forma isolada do destino da solicitação. 

Para aprimorar a usabilidade e precisão do MVP, iremos mapear 19 especialidades clínicas e expandir o catálogo de sintomas. O motor de risco no backend passará a aceitar o `especialidade_id` e a aplicar regras condicionais dinâmicas: um sintoma de gravidade padrão "AMARELO" ou "VERDE" poderá ser elevado para "VERMELHO" ou "AMARELO" dependendo da especialidade médica de destino. No frontend, adicionaremos um seletor dropdown para especialidades e um seletor de autocompletar e tags para a busca de sintomas.

## Goals / Non-Goals

**Goals:**
- Substituir o input de especialidade por uma lista suspensa com 19 especialidades pré-definidas.
- Implementar componente de pesquisa autocomplete reativo para busca de sintomas em `Interconsultas.vue`.
- Atualizar o backend (`RiskEngineService.calcular_gravidade`) para calcular a cor de gravidade com base no par `(sintoma_id, especialidade_id)`.
- Exibir o nome por extenso da especialidade nas tabelas da Central de Marcação.

**Non-Goals:**
- Criar tabelas de banco de dados para gerenciar especialidades ou sintomas. O catálogo continuará estático nas camadas de serviço/store para consistência e agilidade de MVP.

## Decisions

### 1. Mapeamento Estático de Especialidades e IDs
Manter a coluna `especialidade_id` como `Integer` no banco e mapear as especialidades no frontend e backend através de um dicionário/array estático indexado de 1 a 19:
`1: Cardiologia, 2: Clínica Médica, 3: Dermatologia, 4: Endocrinologia, 5: Gastroenterologia, 6: Geriatria, 7: Hematologia, 8: Infectologia, 9: Medicina de Família e Comunidade, 10: Medicina do Trabalho, 11: Nefrologia, 12: Neurologia, 13: Oncologia (CACON), 14: Pediatria, 15: Pneumologia, 16: Psiquiatria, 17: Reumatologia, 18: Urologia, 19: Ginecologia e Obstetrícia`.
- **Racional**: Evita migrations no banco e permite resolver o nome amigável de forma simples no frontend.

### 2. Motor de Risco Dinâmico com Overrides por Especialidade
`RiskEngineService` usará um mapeamento de gravidade padrão para os sintomas e um dicionário de overrides associado ao ID da especialidade:
- **Exemplo**: "Dor torácica intensa" tem gravidade padrão `AMARELO`. No entanto, se o ID da especialidade for `1` (Cardiologia), a gravidade é promovida a `VERMELHO`.
- **Exemplo**: "Ideação suicida ativa" tem gravidade padrão `AMARELO`. Se a especialidade for `16` (Psiquiatria), a gravidade é promovida a `VERMELHO`.

### 3. Autocomplete de Sintomas no Frontend
No template de `Interconsultas.vue`, criaremos um campo de entrada de texto com um menu flutuante reativo filtrando a lista geral de sintomas.
- Quando o usuário digita, mostramos os sintomas correspondentes.
- Ao clicar em um sintoma, ele é adicionado a um array local `sintomasSelecionados` e limpa o texto de busca.
- Os sintomas selecionados serão exibidos em um container flexível como tags com botão (ícone de fechar) para remoção.

## Risks / Trade-offs

- **[Trade-off]** Catálogos estáticos no código exigem novas deploys para alteração.
  - **Mitigação**: Sendo um MVP para validação arquitetural e clínica rápida, o uso de catálogos estáticos acelerará a entrega e evitará a complexidade de tabelas extras.

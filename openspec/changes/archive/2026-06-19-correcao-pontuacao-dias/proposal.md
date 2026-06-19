## Why

Atualmente, as colunas de "pontuação" (score de prioridade) e "tempo de espera" (dias) na Central de Marcação não exibem os valores numéricos dinâmicos, apresentando apenas os sufixos textuais no frontend devido à filtragem do Pydantic no schema de resposta da API do backend. Adicionalmente, a lista de pacientes solicitados está visível na seção de interconsultas (visão do médico), o que expõe indevidamente dados de regulação e viola o princípio de privilégio mínimo da LGPD.

## What Changes

- **Modificação do Backend**: Inclusão dos campos `score_prioridade` (float) e `dias_na_fila` (int) no schema `InterconsultaResponse` para permitir a serialização correta desses dados numéricos dinâmicos gerados pelo `QueueOptimizerService`.
- **Modificação do Painel da Central de Marcação**: Adicionar e exibir corretamente as colunas "Pontuação" (Score) e "Tempo de Espera" (Dias) na tabela de regulação e no painel de detalhes (drawer) da rota `/central-marcacao`.
- **Remoção da Lista na Visão do Médico**: Remover a exibição do card/tabela de "Pedidos ativos" na página de criação de solicitações de interconsultas (`/interconsultas`), restringindo essa visualização de regulação exclusivamente à equipe autorizada na Central de Marcação.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `visualizacao-central-marcacao`: Exibição das métricas de pontuação de prioridade e dias de espera calculadas dinamicamente na fila regulatória da Central de Marcação.
- `encaminhamento-digital`: Restrição de visibilidade da fila e da lista de pacientes para médicos solicitantes, garantindo que a página de solicitação sirva apenas para submissão de novos pedidos.

## Impact

### Fluxo de Dados em Camadas Afetado:
1. **Model/Schema**: Alteração do schema de resposta Pydantic na camada de roteamento/serialização.
2. **Router**: O endpoint `GET /api/interconsultas/` serializará os campos adicionais de prioridade.
3. **Frontend Views**:
   - `CentralMarcacao.vue` consumirá os novos campos serializados e os exibirá em colunas dedicadas.
   - `Interconsultas.vue` deixará de renderizar e buscar a lista de pedidos ativos.

### Arquivos Modificados:
- [MODIFY] [interconsulta_schema.py](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/src/schemas/interconsulta_schema.py)
- [MODIFY] [CentralMarcacao.vue](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/frontend/src/views/CentralMarcacao.vue)
- [MODIFY] [Interconsultas.vue](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/frontend/src/views/Interconsultas.vue)

### Impacto nas Diretrizes LGPD e Trilhas de Auditoria:
- **LGPD**: A remoção da lista de solicitações da visão do médico atende ao princípio de minimização de dados e privilégio mínimo da LGPD, pois impede que usuários sem permissão de regulação (médicos) visualizem dados confidenciais de outros pacientes regulados (incluindo CNS decifrado e diagnósticos presumidos).
- **Auditoria**: A visualização da lista unificada de regulação permanece restrita à equipe de regulação, cujos acessos continuam sendo registrados na trilha de auditoria através do log `AUDITORIA: Usuario ... visualizou os dados sensiveis...` implementado no `InterconsultaController`.

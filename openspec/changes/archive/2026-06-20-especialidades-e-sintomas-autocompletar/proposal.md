## Why

Atualmente, o médico precisa digitar manualmente o ID numérico da especialidade (ex: `1` ou `2`) na criação de uma interconsulta, o que induz a erros operacionais. Além disso, o catálogo de sintomas do MVP é limitado e a gravidade de priorização clínica é inferida puramente a partir de um ID fixo de sintoma, desconsiderando a especialidade solicitada. O fluxo de seleção de sintomas atual por checkboxes torna-se inviável para listas de sintomas maiores. 

Este ajuste implementará uma seleção exata de especialidade via lista suspensa, um catálogo de sintomas rico com funcionalidade de busca e autocompletar no frontend, e regras de priorização no motor de risco que vinculam a gravidade clínica de um sintoma à especialidade correspondente.

## What Changes

- **Seleção Dinâmica de Especialidades**: Substituir a entrada de texto numérico por uma lista suspensa contendo as 19 especialidades recomendadas (Cardiologia, Clínica Médica, Neurologia, etc.).
- **Busca e Autocompletar de Sintomas**: Implementar no formulário de interconsultas um campo de pesquisa para sintomas gerais que sugere termos correspondentes à digitação e adiciona os sintomas selecionados como tags removíveis.
- **Catálogo de Sintomas Expandido**: Expandir o catálogo para incluir múltiplos sintomas relevantes às diversas especialidades (ex: "Ideação suicida ativa", "Paralisia facial", "Dor torácica intensa", etc.).
- **Motor de Risco Vinculado à Especialidade**: Atualizar as regras de classificação clínica de gravidade no backend para considerar a especialidade selecionada (ex: "Dor torácica" em "Cardiologia" é classificado como `VERMELHO`, enquanto em outras especialidades é `AMARELO` ou `VERDE`).
- **Resolução de Nomes na Central**: Ajustar o painel da Central de Marcação para resolver o ID numérico exibindo o nome textual amigável da especialidade.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `encaminhamento-digital`: Seleção e validação do catálogo fixo de especialidades e seleção inteligente de sintomas por autocompletar na interface médica.
- `motor-regras-gravidade`: Classificação inteligente no backend vinculando sintomas e a especialidade de destino.
- `visualizacao-central-marcacao`: Exibição do nome por extenso da especialidade regulada no painel da Central de Marcação.

## Impact

### Fluxo de Dados em Camadas Afetado:
1. **Model**: Mapeamento e serialização das especialidades via IDs no banco de dados.
2. **Controller**: `InterconsultaController.solicitar_interconsulta` passa a passar a especialidade ao motor de classificação de risco.
3. **Risk Engine**: `RiskEngineService.calcular_gravidade` processa a gravidade dinamicamente baseada na especialidade e IDs de sintomas.
4. **Frontend Views**:
   - `Interconsultas.vue` usa dropdown para especialidade e componente de autocomplete para sintomas gerais.
   - `CentralMarcacao.vue` e drawer de detalhes resolvem e exibem o nome da especialidade.

### Arquivos Modificados:
- [MODIFY] [risk_engine_service.py](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/src/services/risk_engine_service.py)
- [MODIFY] [interconsulta_controller.py](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/src/controllers/interconsulta_controller.py)
- [MODIFY] [interconsulta.ts](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/frontend/src/stores/interconsulta.ts)
- [MODIFY] [Interconsultas.vue](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/frontend/src/views/Interconsultas.vue)
- [MODIFY] [CentralMarcacao.vue](file:///c:/Users/sonar/Faculdade/IESI/testeMVP/frontend/src/views/CentralMarcacao.vue)

### Impacto nas Diretrizes LGPD e Trilhas de Auditoria:
- **LGPD**: A melhoria na consistência de dados (nomes de especialidades e seleção exata) reduz o risco de direcionamento de dados confidenciais de pacientes (CNS) para o setor incorreto.
- **Auditoria**: A gravação de logs de auditoria continua inalterada e continuará reportando o acesso de reguladores aos dados do paciente.

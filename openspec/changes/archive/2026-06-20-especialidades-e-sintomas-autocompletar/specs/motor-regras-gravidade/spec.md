## MODIFIED Requirements

### Requirement: Cálculo Automático de Prioridade Clínica
O sistema MUST processar o array de IDs de sintomas contido no pedido e a especialidade solicitada para calcular automaticamente o risco clínico. A priorização clínica de um sintoma MUST ser reavaliada/promovida dinamicamente baseada na especialidade de destino da interconsulta.

#### Scenario: Sintoma de Risco Máximo (Vermelho)
- **WHEN** o array de sintomas contiver ao menos um sintoma classificado como crítico ou cuja gravidade seja promovida a crítico (VERMELHO) na especialidade de destino selecionada
- **THEN** o Motor de Regras atribui a gravidade "VERMELHO" ao pedido antes do envio ao provedor

#### Scenario: Ausência de Sintomas Críticos (Verde)
- **WHEN** o array de sintomas contiver apenas sintomas de baixa gravidade na especialidade de destino
- **THEN** o Motor de Regras atribui a gravidade "VERDE" ao pedido antes do envio

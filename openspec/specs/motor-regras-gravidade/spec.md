# motor-regras-gravidade Specification

## Purpose
TBD - created by archiving change modulo-interconsulta. Update Purpose after archive.
## Requirements
### Requirement: Cálculo Automático de Prioridade Clínica
O sistema MUST processar o array de IDs de sintomas contido no pedido e calcular automaticamente o risco clínico. É expressamente proibida a classificação baseada em texto livre.

#### Scenario: Sintoma de Risco Máximo (Vermelho)
- **WHEN** o array de sintomas contiver ao menos um sintoma classificado nas diretrizes hospitalares como crítico
- **THEN** o Motor de Regras atribui a gravidade "VERMELHO" ao pedido antes do envio ao provedor

#### Scenario: Ausência de Sintomas Críticos (Verde)
- **WHEN** o array de sintomas contiver apenas sintomas de baixa gravidade segundo as diretrizes
- **THEN** o Motor de Regras atribui a gravidade "VERDE" ao pedido antes do envio


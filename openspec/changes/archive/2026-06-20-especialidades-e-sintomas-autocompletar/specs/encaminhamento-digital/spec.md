## ADDED Requirements

### Requirement: Seleção Exata de Especialidade e Autocompletar de Sintomas
O sistema MUST apresentar uma lista suspensa (dropdown) com especialidades clínicas específicas para seleção e um campo de pesquisa reativo (autocomplete) para buscar e selecionar sintomas gerais.

#### Scenario: Preenchimento do Formulário pelo Médico
- **WHEN** o médico acessar a interface de criação de interconsulta
- **THEN** o sistema exibe uma lista suspensa para a seleção exata da especialidade e um campo de entrada de texto com autocompletar que exibe sintomas semelhantes à digitação, adicionando os sintomas escolhidos como tags associadas ao formulário.

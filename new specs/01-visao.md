# Documento de Visão

## 1. Problema e Oportunidade
* **O Problema**: O fluxo de interconsultas é analógico (baseado em papel) e a classificação de risco é falha, pois os médicos não aplicam as diretrizes em PDF durante a prescrição. Além disso, os dados dos processos não são registrados em algum banco pela ausência de digitalização.

* **Impacto**: Pacientes perdem viagens ao HC buscando vagas inexistentes, Médicos solicitantes possuem maior dificuldade de acompanhamento dos casos e a Central de Marcação fica sobrecarregada com processos manuais.
* **Solução Proposta**: Um módulo digital que atua como um portal unificado para o médico. A solução puxa os dados do paciente via API do AGHU e substitui o papel por um formulário digital inteligente. Com base na seleção de sintomas padronizados, um motor de regras interno calcula automaticamente a gravidade clínica e enfileira o pedido diretamente na central de marcação digital do AGHU, salvando um histórico rastreável da solicitação.

## 2. Partes Interessadas (Stakeholders)
* Profissionais assistenciais (médicos solicitantes e especialistas)
* Gestão Hospitalar (central de marcação)

## 3. Escopo do Produto
* Busca rápida de prontuário integrando com a API do AGHU.
* Formulário de interconsulta com mapeamento restrito de sintomas.
* Motor lógico para cálculo automático de gravidade (Alerte de Compliance).
* Fila assíncrona de submissão para a Central de Marcação do AGHU.

## 4. Metas e Objetivos de Negócio
* Redução drástica da ida de pacientes à central de marcação sem obter sucesso no agendamento
* Implementação de uma priorização para casos graves
* Otimização de tempo dos profissionais da central de marcação.
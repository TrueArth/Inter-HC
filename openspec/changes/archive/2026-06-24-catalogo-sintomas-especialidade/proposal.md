## Why

O catálogo de sintomas na área do administrador exibia todos os sintomas cadastrados em uma única lista contínua e imensa, o que dificultava a gestão do administrador. Dividir a visualização de sintomas por especialidade e permitir busca textual rápida melhora significativamente a experiência do usuário e mantém a consistência com outros filtros da aplicação.

## What Changes

* **Abas de Filtragem por Especialidade no Topo:** Implementação de pílulas/botões horizontais no topo do catálogo de sintomas na aba "Sintomas & Regras" da área do administrador, permitindo filtrar os sintomas vinculados a cada especialidade.
* **Campo de Busca de Sintomas:** Inclusão de entrada de texto no topo para busca em tempo real por nome do sintoma.
* **Tags de Especialidades:** Exibição de pequenas tags sob cada sintoma contendo a lista de especialidades vinculadas por regras de gravidade.
* **Pontuação Contextual:** Ajuste para exibir a pontuação do sintoma correspondente à especialidade ativa se uma especialidade estiver selecionada.

## Capabilities

### Modified Capabilities

- `visualizacao-central-marcacao`: Melhoria na visualização de catálogos e regras no painel administrativo.

## Impact

* **Arquivos [MODIFY]:**
  - `frontend/src/views/Admin.vue`
* **Testes:** Verificação da compilação e teste de interface na listagem e alternância de especialidades.

## Why

1. **Consistência de UI/UX**: O alerta padrão do navegador (`window.confirm`) é visualmente destoante do restante da aplicação, que utiliza uma identidade visual rica baseada em Nunito e classes do Tailwind CSS. Substituí-lo por um componente nativo em Vue melhora a experiência do usuário e mantém a identidade visual consistente.
2. **Prevenção de Erros de Operação**: Oferecer uma confirmação explícita com botões "Confirmar" e "Desfazer" contextualizados para cada ação (como Excluir e Reverter) ajuda a Central de Marcação a validar visualmente a ação e o identificador do pedido (ID) que está prestes a ser afetado.

## What Changes

* **Notificação/Confirmação Customizada via Modal**: Substituição dos diálogos `window.confirm` pelas chamadas a um modal dinâmico no Vue para confirmações na Central de Marcação.
* **Exibição do Contexto e Ação**: O modal exibe de forma clara o tipo de ação e o identificador do pedido de interconsulta afetado (ex: "Excluir Solicitação de Interconsulta (ID #123)" ou "Reverter Solicitação de Interconsulta (ID #123)").
* **Fluxo Condicional de Confirmação**: A chamada de API/banco correspondente só é disparada se o usuário clicar no botão "Confirmar". Clicar em "Desfazer" fecha o modal e cancela a ação sem produzir alterações de rede ou banco.

## Capabilities

### Modified Capabilities
- `visualizacao-central-marcacao`: Substitui o uso do `window.confirm` por diálogos de confirmação customizados em Vue para ações de fila (exclusão e reversão de pedidos).

## Impact

### Arquivos Afetados

* **[MODIFY]**
  * `frontend/src/views/CentralMarcacao.vue`

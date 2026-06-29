## Context

A substituição do `window.confirm` pelo modal do Vue é implementada puramente no lado do cliente (Vite/Vue 3) por meio de estados reativos que controlam o ciclo de vida da confirmação.

## Goals / Non-Goals

**Goals:**
* Substituir todas as chamadas nativas de `window.confirm` em `CentralMarcacao.vue` por uma interface de confirmação em Vue.
* Reaproveitar o componente `Modal.vue` já existente no frontend.
* Expor botões de ação explícitos "Confirmar" e "Desfazer".
* Exibir a ação pendente contendo o ID da interconsulta afetada (ex: `Excluir Solicitação de Interconsulta (ID #12)`) no título ou corpo do modal.

**Non-Goals:**
* Não implementar timers ou contagem regressiva para fechar o modal ou disparar a ação automaticamente.
* Não alterar o comportamento de rede caso o usuário clique em "Desfazer".

## Decisions

### 1. Reuso do Componente `Modal.vue`
Utilizaremos o componente modal global `<Modal>` para renderizar a janela de confirmação de maneira consistente com o layout geral (ex.: cabeçalhos, rodapés e efeitos de transição/blur).

### 2. Estados de Confirmação na View
Criamos estados reativos na view `CentralMarcacao.vue` para governar o conteúdo e a visibilidade do modal:
```typescript
const mostrarModalConfirmacao = ref(false);
const tituloConfirmacao = ref('');
const mensagemConfirmacao = ref('');
const tipoConfirmacao = ref<'excluir' | 'reverter'>('excluir');
let acaoConfirmadaCallback: (() => Promise<void>) | null = null;
```

### 3. Callback Dinâmico para Ação
A função `abrirConfirmacao(...)` recebe a configuração da notificação e uma função de callback (promessa). Se o botão "Confirmar" for pressionado, o callback é executado (chamada do backend), caso contrário, o callback é descartado limpando o estado na memória.

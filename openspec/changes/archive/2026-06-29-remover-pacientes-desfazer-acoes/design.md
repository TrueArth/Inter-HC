## Context

A funcionalidade de "Desfazer Ação" (Undo) é implementada puramente no lado do cliente (Vite/Vue 3) para evitar poluição e complexidade desnecessária no banco de dados local.

## Goals / Non-Goals

**Goals:**
* Reter chamadas de API de escrita (`criarPedido`, `atualizarStatusPedido`, `reprocessarPedido`) por 30 segundos.
* Apresentar contagem regressiva reativa e botão de desfazer no layout principal (`DefaultLayout.vue`).
* Remover todo e qualquer atalho ou visualização de pacientes do painel de administração.

**Non-Goals:**
* Não será persistido estado de desfazer caso a página seja recarregada (`F5`) ou fechada; a ação pendente será perdida e não executada.

## Decisions

### 1. Store Global de Desfazer (Pinia)
Criaremos um estado reativo na store `useInterconsultaStore` para conter a ação ativa que pode ser desfeita:
```typescript
interface UndoAction {
  id: string;
  name: string;
  execute: () => Promise<void>;
  cancel?: () => void;
  secondsLeft: number;
}
```

### 2. UI Banner de Contagem
No layout principal (`DefaultLayout.vue`), renderizamos um banner fixo `fixed bottom-6 right-6 z-50` com animação suave de transição e um SVG dinâmico exibindo a contagem circular dos 30 segundos restantes.

### 3. Remoção de Rota
No roteador Vue (`frontend/src/router/index.ts`), o mapeamento da rota `/pacientes` será excluído e seu import apagado. O arquivo correspondente `frontend/src/views/Pacientes.vue` será removido fisicamente da base de código.

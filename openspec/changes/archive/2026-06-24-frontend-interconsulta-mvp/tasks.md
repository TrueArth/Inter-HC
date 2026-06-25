## 1. Store e tipos (Pinia)

- [x] 1.1 Criar `frontend/src/stores/interconsulta.ts` com interfaces TypeScript para payload e resposta da API.
- [x] 1.2 Definir constante `SINTOMAS_CATALOGO_MVP` (IDs 1–6 alinhados ao `RiskEngineService`) exportada pelo store ou arquivo de constantes.
- [x] 1.3 Implementar `criarPedido(payload)` chamando `POST /api/interconsultas/` via `api.ts`.
- [x] 1.4 Implementar `listarPedidos()` chamando `GET /api/interconsultas/` e estado `loading` / tratamento de erro.
- [x] 1.5 Implementar helper `mascararCns(cns: string)` para exibição na tabela.

## 2. View e componentes

- [x] 2.1 Criar `frontend/src/views/Interconsultas.vue` com Card de formulário (CNS, especialidade_id, checkboxes de sintomas, botão enviar com `:loading`).
- [x] 2.2 Adicionar validação client-side (CNS 15 dígitos, especialidade ≥ 1, ≥ 1 sintoma) antes do POST.
- [x] 2.3 Implementar tabela de pedidos com chips de gravidade (VERMELHO/AMARELO/VERDE) e CNS mascarado.
- [x] 2.4 Integrar `vue-toastification` para sucesso (incluir gravidade) e erros de API.
- [x] 2.5 Chamar `listarPedidos` no `onMounted` e após POST bem-sucedido; limpar formulário após criar.

## 3. Roteamento e navegação

- [x] 3.1 Registrar rota `/interconsultas` em `frontend/src/router/index.ts` com `meta: { requiresAuth: true }`.
- [x] 3.2 Adicionar link "Interconsultas" no menu de `frontend/src/layouts/DefaultLayout.vue` (visível para usuário autenticado).

## 4. Verificação manual

- [x] 4.1 Build do frontend (`npm run build` no diretório `frontend`) sem erros TypeScript.
- [x] 4.2 Teste manual: login → `/interconsultas` → criar pedido com sintoma id=1 → verificar badge VERMELHO na lista.
- [x] 4.3 Teste manual: acesso sem login redireciona para `/login`.

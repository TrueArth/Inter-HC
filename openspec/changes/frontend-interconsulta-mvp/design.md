## Context

O backend de interconsulta está implementado (`/api/interconsultas` com POST, GET, DELETE), incluindo `RiskEngineService`, criptografia de CNS e fila assíncrona. O frontend Vue 3 já possui autenticação JWT (`stores/auth.ts`, `services/api.ts` com interceptors), padrões de tela em `Leitos.vue` / `Pacientes.vue`, e proxy Vite para `/api`. Não há rota, store ou view de interconsulta.

## Goals / Non-Goals

**Goals:**

- Entregar rota autenticada `/interconsultas` com formulário e listagem na mesma página.
- Consumir APIs existentes sem alterar contrato backend.
- Catálogo estático de sintomas (IDs 1–6) alinhado a `SINTOMAS_CRITICOS_IDS` e `SINTOMAS_MODERADOS_IDS` no backend.
- Feedback visual de gravidade e status retornados pelo servidor após POST.
- Mascaramento de CNS na tabela (`***` + últimos 4 dígitos).

**Non-Goals:**

- Integração AGHU para paciente ou especialidade dinâmica.
- Preview de gravidade calculada no browser antes do POST.
- Cancelamento via `DELETE` na UI.
- Testes E2E automatizados (apenas checklist manual neste MVP).
- Alterações em SQL, Provider, Controller ou Router backend.

## Decisions

### 1. Uma rota, uma view (`Interconsultas.vue`)

**Escolha:** Formulário superior + tabela inferior, espelhando `Leitos.vue`.

**Alternativa rejeitada:** Wizard multi-step — desnecessário sem contexto de prontuário AGHU.

### 2. Pinia store dedicada

**Escolha:** `useInterconsultaStore` com `criarPedido`, `listarPedidos`, `loading`, `error`.

**Alternativa rejeitada:** Lógica só na view — dificulta reuso e testes futuros.

### 3. Catálogo de sintomas constante no front

**Escolha:** Array exportado em `stores/interconsulta.ts` ou `constants/sintomasCatalog.ts` com `{ id, nome, tier }` para labels; envio como `{ id, nome }[]` no POST.

**Rationale:** Backend não expõe `GET /sintomas`; duplicar IDs evita drift até API de catálogo existir. Documentar comentário referenciando `RiskEngineService`.

### 4. `medico_solicitante_crm` no payload

**Escolha:** Enviar `"-"` no POST; servidor sobrescreve com `current_user.name` do JWT.

### 5. Validação client-side

**Escolha:** Bloquear submit se CNS ≠ 15 dígitos, `especialidade_id < 1`, ou zero sintomas; usar `vue-toastification` para erros de API (padrão `Pacientes.vue`).

### 6. Componentes UI

**Escolha:** `Card`, `Button`, tabela HTML simples, classes `form-control` / `form-label` existentes. Chips Tailwind para `VERMELHO` / `AMARELO` / `VERDE`.

**Alternativa rejeitada:** `DataTable` com ações — escopo v2.

### 7. Fluxo de dados (frontend)

```
Interconsultas.vue
    → useInterconsultaStore
        → api.ts (Bearer JWT)
            → FastAPI Router → Controller → Provider
```

Sem bypass de camadas backend; front é consumidor HTTP apenas.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Catálogo front diverge do `RiskEngineService` | IDs 1–6 documentados; comentário no código; teste manual com sintoma id=1 → VERMELHO |
| CNS exibido em claro no formulário pós-submit | Limpar campo após sucesso; mascarar na tabela |
| `especialidade_id` numérico opaco para o médico | Aceito no MVP; label "Código da especialidade (AGHU)" |
| Sem testes automatizados de UI | Checklist manual nos critérios de aceite da spec |

## Migration Plan

1. Implementar store + view + router + nav.
2. `npm run build` no frontend (ou script do projeto) para gerar bundle em `src/static/dist`.
3. Verificar manualmente com backend local: login → `/interconsultas` → POST → lista atualizada.
4. Rollback: remover rota e arquivos novos; sem migração de banco.

## Open Questions

- Ícone do menu lateral (reutilizar `UsersIcon` ou adicionar ícone clínico) — decisão cosmética na implementação.
- Internacionalização de labels — fora de escopo; manter PT-BR como demais views.

## Context

Atualmente, o backend calcula a pontuação dinâmica (`score_prioridade`) e dias na fila (`dias_na_fila`) no `QueueOptimizerService` e os injeta nos objetos de pedido no controlador. No entanto, o roteador do FastAPI filtra o retorno usando o schema `InterconsultaResponse`, que não inclui esses campos, fazendo com que o frontend receba os campos como `undefined`.
Além disso, a visualização `/interconsultas` (destinada a médicos solicitantes) renderiza uma tabela com todas as solicitações ativas do banco de dados local. Isso gera exposição desnecessária de dados clínicos e CNS (violação das boas práticas de LGPD / privilégio mínimo) e confunde a função do médico solicitante com a da Central de Marcação.

## Goals / Non-Goals

**Goals:**
- Garantir que a pontuação (`score_prioridade`) e dias na fila (`dias_na_fila`) sejam retornados numericamente pela API e exibidos adequadamente no painel `/central-marcacao`.
- Restringir a página `/interconsultas` para ser apenas o formulário de cadastro, removendo a tabela de "Pedidos ativos" e a chamada ao endpoint correspondente nessa rota.

**Non-Goals:**
- Alterar o motor de cálculo de risco (`RiskEngineService` ou `QueueOptimizerService`).
- Criar novos endpoints ou modificar as políticas de autenticação LDAP/AD existentes.

## Decisions

### 1. Inclusão dos campos de prioridade no Pydantic Schema
Adicionar `score_prioridade: Optional[float] = None` e `dias_na_fila: Optional[int] = None` ao schema `InterconsultaResponse`.
- **Alternativa Considerada**: Criar um novo schema `InterconsultaRegulatorResponse`. **Decisão**: Reutilizar `InterconsultaResponse` simplifica a base de código uma vez que ambos os fluxos compartilham a mesma entidade no backend e as permissões de acesso a dados confidenciais (CNS) são tratadas no nível do controlador.

### 2. Adição de colunas na tabela da Central de Marcação
Inserir as colunas "Pontuação" e "Tempo de Espera" na tabela e no painel lateral de detalhes em `CentralMarcacao.vue`.
- **Visual**: "Pontuação" exibirá `{{ pedido.score_prioridade }} pts` e "Tempo de Espera" exibirá `{{ pedido.dias_na_fila }} dias`.

### 3. Remoção do componente de lista em `Interconsultas.vue`
Remover a tabela de "Pedidos ativos" do template do componente e a chamada a `recarregar()` no `onMounted` de `Interconsultas.vue`.
- **Segurança**: Minimiza chamadas de rede desnecessárias por parte de usuários com papel de médico.

## Risks / Trade-offs

- **[Risco]** Acesso direto à API por médicos ainda retornará a lista se o endpoint `GET /api/interconsultas/` não for bloqueado.
  - **Mitigação**: O controlador `listar_pedidos` já possui logs de auditoria LGPD integrados para monitorar visualizações de CNS. A restrição na UI é o foco imediato deste MVP para separar as visões de negócios.

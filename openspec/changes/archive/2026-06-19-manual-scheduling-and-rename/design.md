## Context

Atualmente, o fluxo de criação de interconsultas invoca automaticamente o worker assíncrono `enviar_para_central_aghu` via `MessageBroker.dispatch`. A nova diretriz de negócio exige que todos os pedidos submetidos fiquem estritamente em estado `PENDENTE`, aguardando a triagem e ação manual da Central de Marcação para efetivar o agendamento no legado.
Além disso, a marca de identificação visual "My App" deve ser alterada para a denominação oficial "InterHC".

## Goals / Non-Goals

**Goals:**
- Modificar o status inicial de novas solicitações para `PENDENTE` no controller do backend.
- Remover o disparo de fila assíncrona automático do broker na submissão de novos pedidos.
- Renomear todos os pontos visíveis da marca "My App" para "InterHC" no frontend.

**Non-Goals:**
- Remover o endpoint de retry manual (`/api/interconsultas/{pedido_id}/retry`) ou a capacidade de envio do worker, que continuam válidos para disparos manuais.

## Decisions

### 1. Modificar status padrão e remover dispatch no Controller
Em `src/controllers/interconsulta_controller.py`, alterar `payload["status"] = "ENFILEIRADO"` para `"PENDENTE"`. Remover/comentar a linha de publicação no broker:
```python
# MessageBroker.dispatch(background_tasks, enviar_para_central_aghu, pedido_criado)
```
- **Racional**: Garante que o pedido seja inserido na base de dados local apenas como `PENDENTE`, sem gerar tráfego automático para a API externa ou fila de envio até intervenção regulatória.

### 2. Alteração de String do Logo e Títulos do Frontend
Modificar `frontend/src/layouts/DefaultLayout.vue` e `frontend/index.html` substituindo "My App" por "InterHC".

## Risks / Trade-offs

- **[Risco]** A fila manual pode acumular se a equipe de regulação não monitorar o painel ativamente.
  - **Mitigação**: O painel da Central de Marcação exibe alertas visuais claros de pedidos aguardando regulação.

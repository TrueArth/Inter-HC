## 1. Backend Implementation - Data Layer (SQL & Provider)

- [x] 1.1 Criar o arquivo SQL `atualizar_status_pedido.sql` no diretório `src/providers/sql/interconsulta/`
- [x] 1.2 Atualizar `InterconsultaProviderInterface` para adicionar o método `atualizar_status_pedido(pedido_id: int, novo_status: str)`
- [x] 1.3 Implementar o método `atualizar_status_pedido` no `InterconsultaPostgresProvider`
- [x] 1.4 Implementar o método `atualizar_status_pedido` no `InterconsultaMockProvider`

## 2. Backend Implementation - Business & Routing Layers

- [x] 2.1 Atualizar `InterconsultaController` para adicionar métodos para alteração de status e re-enfileiramento (retry manual)
- [x] 2.2 Atualizar o roteador `interconsulta.py` adicionando os endpoints `PATCH /api/interconsultas/{pedido_id}/status` e `POST /api/interconsultas/{pedido_id}/retry`
- [x] 2.3 Adicionar registro detalhado de log de auditoria no controlador/roteador quando os dados do CNS forem decifrados para os reguladores
- [x] 2.4 Integrar no worker `central_marcacao_worker.py` a atualização automática do status no banco para 'PENDENTE' ou 'ERRO' usando o Postgres provider

## 3. Frontend Implementation - Router & Store

- [x] 3.1 Adicionar novas rotas no Vue router em `frontend/src/router/index.ts` para `/central-marcacao` com verificação de login
- [x] 3.2 Atualizar o layout principal `frontend/src/layouts/DefaultLayout.vue` para incluir o link para o painel de regulação na barra lateral
- [x] 3.3 Estender a store Pinia do interconsulta (ou criar uma nova) no frontend para lidar com a busca de fila geral, atualização de status e ações de retry manual

## 4. Frontend Implementation - Views & Components

- [x] 4.1 Criar a view reativa `frontend/src/views/CentralMarcacao.vue` com a listagem ordenada de pedidos e exibição de detalhes e sintomas
- [x] 4.2 Adicionar ações no painel (atualizar status para 'AGENDADO' e botão "Re-enviar" em caso de status 'ERRO')
- [x] 4.3 Aplicar regras visuais premium de design na tabela e nos badges de gravidade clínica e status

## 5. Verification & Tests

- [x] 5.1 Criar e rodar testes automatizados para verificar a atualização de status no provider
- [x] 5.2 Testar manualmente o fluxo de criação de pedido, visualização no painel de regulação, e re-envio manual do worker

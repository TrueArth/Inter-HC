## 1. Backend Adjustments

- [x] 1.1 Modificar `InterconsultaController.solicitar_interconsulta` em `src/controllers/interconsulta_controller.py` para definir o status como `PENDENTE` na criação.
- [x] 1.2 Remover o disparo de fila assíncrona automática (`MessageBroker.dispatch`) na submissão médica em `src/controllers/interconsulta_controller.py`.
- [x] 1.3 Atualizar ou adicionar testes unitários para validar que novos pedidos de interconsulta iniciam como `PENDENTE` e não disparam agendamento automático.

## 2. Frontend Rename & Brand updates

- [x] 2.1 Renomear "My App" para "InterHC" em `frontend/src/layouts/DefaultLayout.vue` (no menu móvel e logotipo lateral).
- [x] 2.2 Renomear a tag `<title>` para "InterHC" em `frontend/index.html`.

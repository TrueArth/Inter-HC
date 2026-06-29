## 1. Documentação (OpenSpec)
- [ ] Criar especificações e propostas em `openspec/changes/2026-06-29-remover-pacientes-desfazer-acoes/`
- [ ] Atualizar especificações globais `specs/encaminhamento-digital/spec.md` e `specs/visualizacao-central-marcacao/spec.md`

## 2. Frontend - Remoção de Pacientes
- [ ] Excluir rota de pacientes em `frontend/src/router/index.ts`
- [ ] Remover link do menu lateral em `frontend/src/layouts/DefaultLayout.vue`
- [ ] Remover card da dashboard em `frontend/src/views/Home.vue`
- [ ] Excluir fisicamente o arquivo `frontend/src/views/Pacientes.vue`

## 3. Frontend - Mecanismo de Desfazer (30s)
- [ ] Implementar `registerUndoableAction` e `triggerUndo` na store `frontend/src/stores/interconsulta.ts`
- [ ] Adicionar banner flutuante no `DefaultLayout.vue`
- [ ] Enfileirar submissão de formulário com desfazer em `frontend/src/views/Interconsultas.vue`
- [ ] Enfileirar agendamento e retentativas em `frontend/src/views/CentralMarcacao.vue`

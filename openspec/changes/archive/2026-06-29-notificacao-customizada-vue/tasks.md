## 1. Documentação (OpenSpec)
- [x] Criar especificações e propostas em `openspec/changes/notificacao-customizada-vue/`

## 2. Frontend - Integração do Modal de Confirmação Customizado
- [x] Declarar variáveis de estado reativas (`mostrarModalConfirmacao`, `tituloConfirmacao`, etc.) no script setup de `frontend/src/views/CentralMarcacao.vue`
- [x] Implementar funções auxiliares `abrirConfirmacao`, `cancelarConfirmacao` e `executarConfirmacao`
- [x] Inserir a marcação do componente `<Modal>` customizado no template de `CentralMarcacao.vue`
- [x] Atualizar as chamadas de exclusão (`cancelarEExcluirPedido`) para usar o novo fluxo com o título `Excluir Solicitação de Interconsulta (ID #id)`
- [x] Atualizar as chamadas de reversão (`reverterPedido`) para usar o novo fluxo com o título `Reverter Solicitação de Interconsulta (ID #id)`
- [x] Validar que o clique em "Desfazer" apenas fecha o modal e cancela a execução, e que o botão de "Confirmar" executa as chamadas ao backend

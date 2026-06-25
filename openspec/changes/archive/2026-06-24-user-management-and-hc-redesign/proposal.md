## Why

O sistema necessita de isolamento de papéis mais rigoroso (médicos e reguladores em suas respectivas telas), exclusão de seções de exemplo, e adequação visual à identidade do Hospital das Clínicas da UFPE (HC-UFPE). Adicionalmente, é necessário corrigir a exibição de sintomas na Central de Marcação, fornecer uma interface de administração de usuários locais (CRUD) e registrar qual regulador realizou a marcação da consulta para auditoria.

## What Changes

* **Redesenho Visual (HC-UFPE):** Atualização do tema de cores no frontend, utilizando tons de azul (primary, brand, sidebar) alinhados à identidade do HC da UFPE.
* **Remoção de Exemplos:** Exclusão da rota e menu "Exemplos" em todo o sistema.
* **Gestão de Usuários pelo Admin:** Criação de interface CRUD no painel do administrador para listar, criar, editar e desativar usuários.
* **Visão Geral e Controle de Acesso (Role Isolation):** 
  * O perfil `admin` pode visualizar todas as telas (/admin, /interconsultas, /central-marcacao).
  * O perfil `medico` tem acesso exclusivo a `/interconsultas`.
  * O perfil `regulador` tem acesso exclusivo a `/central-marcacao`.
  * Bloqueio visual e por rotas de navegação (guards) no frontend e autenticação do backend.
* **Correção de Sintomas Detalhados:** Correção no backend e frontend para exibir corretamente os sintomas selecionados pelo médico no drawer de detalhes na Central de Marcação.
* **Identificação do Marcador (Auditoria):** Registro do nome de usuário do regulador que realiza o agendamento no campo `marcado_por` do banco de dados e exibição desse dado no detalhamento da consulta.

## Capabilities

### New Capabilities
- `user-management`: Permite a criação e gestão de usuários administrativos e clínicos locais no banco de dados da aplicação pelo usuário Administrador.

### Modified Capabilities
- `visualizacao-central-marcacao`: Requisitos de visualização de sintomas na central, exibição do marcador no agendamento e isolamento de acesso à central apenas para reguladores e admin.
- `encaminhamento-digital`: Requisitos de isolamento de acesso à tela de solicitações apenas para médicos e admin.

## Impact

### Fluxo de Dados em Camadas (CRUD de Usuários)
Seguindo o fluxo obrigatório: `SQL ➔ Resource ➔ Provider ➔ Controller ➔ Router`
* **SQL:** Criação das queries de inserção, listagem, atualização e desativação de usuários em `src/providers/sql/user/`.
* **Resource:** Utilização de `get_app_db_session` em `src/resources/database.py` para obter conexões.
* **Provider:** Criação de `UserPostgresProvider` e `UserMockProvider` para execução dos SQLs.
* **Controller:** Criação de `UserController` para lógica de criptografia de senhas e validações.
* **Router:** Criação/ajuste de endpoints em `/api/admin/users` no router `src/routers/admin.py`.

### Arquivos Afetados

* **[NEW]**
  * `src/models/user.py`
  * `src/providers/interfaces/user_provider_interface.py`
  * `src/providers/implementations/user_postgres_provider.py`
  * `src/providers/implementations/user_mock_provider.py`
  * `src/controllers/user_controller.py`
  * `src/providers/sql/user/inserir_usuario.sql`
  * `src/providers/sql/user/listar_usuarios.sql`
  * `src/providers/sql/user/atualizar_usuario.sql`
  * `src/providers/sql/user/deletar_usuario.sql`
  * `frontend/src/views/AdminUsers.vue`
* **[MODIFY]**
  * `src/models/interconsulta.py` (coluna `marcado_por`)
  * `src/schemas/interconsulta_schema.py` (campo `sintomas_json` e `marcado_por` no `InterconsultaResponse`)
  * `src/routers/admin.py` (adicionar rotas CRUD de usuários)
  * `src/routers/interconsulta.py` (atualizar PATCH de status com `current_user` e auditoria)
  * `src/auth/auth.py` (verificação de credenciais no banco local como fallback se não houver AD/LDAP real)
  * `frontend/src/index.css` (tema azul e HC-UFPE)
  * `frontend/src/router/index.ts` (retirar Exemplos, aplicar route guards de papéis)
  * `frontend/src/layouts/DefaultLayout.vue` (retirar Exemplos, filtrar links de menu baseados em papéis)
  * `frontend/src/views/Admin.vue` (integrar CRUD de usuários ou redirecionar)
  * `frontend/src/views/CentralMarcacao.vue` (exibir sintomas no drawer e o marcador responsável)

### LGPD e Trilhas de Auditoria
* O CNS do paciente continua criptografado via AES-256 em trânsito e em repouso no banco.
* O novo campo `marcado_por` registra de forma permanente o operador responsável pelo agendamento, sendo registrado também na trilha de log do sistema (`logger.warning("AUDITORIA: ...")`).

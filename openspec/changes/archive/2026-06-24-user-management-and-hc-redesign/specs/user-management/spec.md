## ADDED Requirements

### Requirement: CRUD de Usuários para Administrador
O sistema MUST disponibilizar uma interface de administração exclusiva para o perfil 'admin' que permita listar, criar, editar e desativar usuários locais da aplicação. Os novos usuários cadastrados devem possuir credenciais salvas de forma segura no banco de dados local da aplicação e estar vinculados a um dos papéis válidos: 'admin', 'medico', 'regulador'.

#### Scenario: Criação de novo usuário com sucesso pelo administrador
- **WHEN** o administrador envia o formulário com username, senha, display name, papel e e-mail
- **THEN** o sistema valida e persiste as informações, encriptando a senha, e retorna status 201 Created

#### Scenario: Listagem de usuários pelo administrador
- **WHEN** o administrador acessa a tela de gerenciamento de usuários
- **THEN** o sistema retorna e exibe a lista de todos os usuários cadastrados cujas contas não foram desativadas (sem Soft Delete aplicado)

#### Scenario: Atualização de dados de usuário
- **WHEN** o administrador edita as informações de um usuário existente
- **THEN** o sistema atualiza os dados no banco de dados e reflete as mudanças na interface

#### Scenario: Inativação de usuário (Soft Delete)
- **WHEN** o administrador solicita a desativação de um usuário
- **THEN** o sistema aplica o Soft Delete definindo a data de inativação em `deleted_at` e oculta o usuário da listagem ativa

### Requirement: Restrição de Acesso às Telas por Papel (Role Isolation)
O sistema MUST restringir o acesso às rotas do sistema com base nas credenciais JWT e papéis do usuário conectado. A rota `/admin` deve ser acessada exclusivamente pelo perfil 'admin'. As rotas de médicos e reguladores devem ser isoladas.

#### Scenario: Acesso restrito a rota de admin
- **WHEN** um usuário não-admin tenta acessar a rota `/admin`
- **THEN** o sistema bloqueia o acesso redirecionando o usuário e retornando erro 403 Forbidden nas APIs correspondentes

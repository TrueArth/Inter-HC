## 1. Banco de Dados e Modelos (SQL/Resource/Models)

- [ ] 1.1 Criar modelo de usuário `User` em `src/models/user.py`
- [ ] 1.2 Atualizar o modelo `InterconsultaPedido` em `src/models/interconsulta.py` para incluir a coluna `marcado_por`
- [ ] 1.3 Criar arquivos SQL nativos para gestão de usuários na pasta `src/providers/sql/user/` (inserir, listar, atualizar, deletar)
- [ ] 1.4 Atualizar as queries SQL de interconsulta para incluir `marcado_por` na inserção, listagem e atualização de status

## 2. Providers e Controllers (Provider/Controller)

- [ ] 2.1 Implementar a interface `UserProviderInterface` e suas implementações `UserPostgresProvider` e `UserMockProvider`
- [ ] 2.2 Implementar o `UserController` com a lógica de negócio do CRUD e hash de senhas com bcrypt
- [ ] 2.3 Ajustar o provedor de autenticação em `src/auth/auth.py` para consultar a tabela de usuários locais

## 3. Routers e Validações (Router)

- [ ] 3.1 Adicionar endpoints do CRUD de usuários em `src/routers/admin.py` protegidos por verificação de administrador
- [ ] 3.2 Atualizar o endpoint de status em `src/routers/interconsulta.py` para receber a identificação do regulador e persistir em `marcado_por`
- [ ] 3.3 Atualizar o schema Pydantic `InterconsultaResponse` para incluir `sintomas_json` e `marcado_por`
- [ ] 3.4 Criar testes de integração para o CRUD de usuários e permissões de acesso

## 4. Frontend e Interface (Frontend)

- [ ] 4.1 Modificar o tema de cores em `frontend/src/index.css` para a paleta de azuis e identidade do HC-UFPE
- [ ] 4.2 Remover a opção "Exemplos" do router e menu de navegação lateral
- [ ] 4.3 Implementar route guards baseados em papéis de usuário no frontend e condicionar exibição de menus
- [ ] 4.4 Criar componente de gerenciamento de usuários no menu Admin (`AdminUsers.vue`)
- [ ] 4.5 Ajustar a Central de Marcação para exibir os sintomas detalhados no drawer e a identificação do regulador agendador

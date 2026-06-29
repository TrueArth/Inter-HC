## 1. Banco de Dados e Modelos (SQL/Resource/Models)

- [ ] 1.1 Criar arquivo de migração do Alembic para adicionar `paciente_contato` em `interconsulta_pedidos`
- [ ] 1.2 Atualizar o modelo SQLAlchemy `InterconsultaPedido` em `src/models/interconsulta.py`
- [ ] 1.3 Adicionar coluna nos SQL templates nativos em `src/providers/sql/interconsulta/` (inserir e listar)

## 2. Providers e Controllers (Provider/Controller)

- [ ] 2.1 Atualizar `InterconsultaPostgresProvider` e `InterconsultaMockProvider` para encriptar/decriptar `paciente_contato`
- [ ] 2.2 Atualizar seed de teste e migrações SQLite automáticas no startup (`src/main.py`)

## 3. Routers e Validações (Router)

- [ ] 3.1 Atualizar schemas Pydantic em `src/schemas/interconsulta_schema.py`
- [ ] 3.2 Atualizar exportação de Excel no router administrativo `src/routers/admin.py`

## 4. Frontend e Interface (Frontend)

- [ ] 4.1 Mapear `paciente_contato` nos tipos e validar na store Pinia `frontend/src/stores/interconsulta.ts`
- [ ] 4.2 Adicionar campo de telefone de contato na interface do médico (`frontend/src/views/Interconsultas.vue`)
- [ ] 4.3 Exibir a coluna de contato e Drawer de detalhes na central de regulação (`frontend/src/views/CentralMarcacao.vue`)

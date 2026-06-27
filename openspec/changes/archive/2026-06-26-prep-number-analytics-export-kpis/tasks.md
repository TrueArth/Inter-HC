## 1. Banco de Dados e Modelos (SQL/Resource/Models)

- [ ] 1.1 Gerar arquivo de migração do Alembic para renomear `paciente_cns` para `paciente_prep` em `interconsulta_pedidos`
- [ ] 1.2 Atualizar o modelo SQLAlchemy `InterconsultaPedido` em `src/models/interconsulta.py` para utilizar `paciente_prep`
- [ ] 1.3 Renomear colunas e referências nos SQL templates nativos em `src/providers/sql/interconsulta/` (inserir e listar)

## 2. Providers e Controllers (Provider/Controller)

- [ ] 2.1 Atualizar `InterconsultaPostgresProvider` e `InterconsultaMockProvider` para usar `paciente_prep` ao invés de `paciente_cns`
- [ ] 2.2 Alterar método `resolver_nome_por_cns` para `resolver_nome_por_prep` em `src/controllers/interconsulta_controller.py` e ajustar leitura de CSV
- [ ] 2.3 Atualizar os dados dos arquivos `data/pacientes.csv` e `data/interconsultas.json` substituindo CNS por valores de PREP com 7-8 dígitos
- [ ] 2.4 Atualizar scripts de seed em `src/main.py` para popular `paciente_prep` com dados criptografados válidos

## 3. Routers e Validações (Router)

- [ ] 3.1 Instalar e declarar a dependência `openpyxl` no `requirements.txt` e `pyproject.toml`
- [ ] 3.2 Atualizar o schema Pydantic `InterconsultaCreate` em `src/schemas/interconsulta_schema.py` para aceitar `paciente_prep` e aplicar validação de 7-8 dígitos
- [ ] 3.3 Atualizar o schema Pydantic `InterconsultaResponse` e ajustar todos os locais de referência no router de interconsultas
- [ ] 3.4 Estender `/api/admin/statistics` em `src/routers/admin.py` com os KPIs: tempo médio de atendimento e ranking de especialidades com mais pendências
- [ ] 3.5 Criar o endpoint `/api/admin/statistics/export` em `src/routers/admin.py` para gerar e fazer streaming do arquivo Excel (.xlsx)

## 4. Frontend e Interface (Frontend)

- [ ] 4.1 Atualizar o store `frontend/src/stores/interconsulta.ts` para mapear `paciente_prep` e validar dígitos entre 7 e 8
- [ ] 4.2 Alterar tela de solicitação de médico `frontend/src/views/Interconsultas.vue` para rotular o campo como PREP e validar o tamanho
- [ ] 4.3 Ajustar a Central de Marcação `frontend/src/views/CentralMarcacao.vue` para usar `pedido.paciente_prep` e exibir "PREP do Paciente"
- [ ] 4.4 Modificar o painel `frontend/src/views/Admin.vue` para exibir os novos KPIs: "Total de Interconsultas", "Tempo Médio de Atendimento" e o ranking de "Especialidades com Mais Pendências"
- [ ] 4.5 Adicionar o botão "Exportar para Excel" na aba de Estatísticas de `frontend/src/views/Admin.vue` integrado com a API

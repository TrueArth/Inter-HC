## Why

A central de regulação e os médicos solicitantes necessitam de uma forma de contato direto com o paciente regulado em caso de reagendamentos, dúvidas clínicas rápidas ou orientações pré-consulta. A inclusão do número de contato telefônico do paciente, opcionalmente fornecido pelo médico assistente no momento da interconsulta, atende a essa demanda e agiliza o fluxo regulatório.

## What Changes

* **Contato do Paciente Opcional:** Adição de campo de entrada opcional no formulário de encaminhamento do médico para número de telefone do paciente.
* **Formatação Flexível:** Suporte aos formatos brasileiro `(dd) xxxxx-xxxx` ou `(dd) xxxx-xxxx`, com ou sem espaços.
* **Exibição na Central de Marcação:** Adição da coluna "Contato" na listagem de regulação da Central de Marcação e também na visualização de detalhes (Drawer).
* **Exportação Administrativa:** Inclusão do telefone de contato decifrado na aba de exportação para Excel (perfil admin).

## Capabilities

### Modified Capabilities
- `encaminhamento-digital`: Ajustado para permitir a entrada opcional e validação de `paciente_contato`.
- `visualizacao-central-marcacao`: Ajustado para expor a coluna e detalhe de `paciente_contato` na Central de Marcação.
- `analytics-export`: Ajustado para conter a coluna `"Contato Paciente"` na planilha Excel exportada.

## Impact

### Fluxo de Dados em Camadas
Seguindo o fluxo regulamentado de camadas: `SQL ➔ Resource ➔ Provider ➔ Controller ➔ Router`
- **SQL:** Atualização de `inserir_pedido.sql` e `listar_pedidos.sql` em `src/providers/sql/interconsulta/` para referenciar a coluna `paciente_contato`.
- **Resource:** Geração de migração Alembic para adicionar a coluna `paciente_contato` na tabela `interconsulta_pedidos`.
- **Provider:** Implementação da criptografia AES-256 no campo `paciente_contato` nas classes do Postgres e do Mock Provider.
- **Controller:** Passagem direta do payload e resolução do contato descriptografado.
- **Router:** Inclusão nos schemas de criação/resposta do Pydantic, e inclusão na exportação Excel do Admin.

### Arquivos Afetados

* **[NEW]**
  * `alembic/versions/f73e5f2a1b9c_add_paciente_contato.py`
* **[MODIFY]**
  * `src/models/interconsulta.py`
  * `src/schemas/interconsulta_schema.py`
  * `src/providers/sql/interconsulta/inserir_pedido.sql`
  * `src/providers/sql/interconsulta/listar_pedidos.sql`
  * `src/providers/implementations/interconsulta_postgres_provider.py`
  * `src/providers/implementations/interconsulta_mock_provider.py`
  * `src/routers/admin.py`
  * `src/main.py`
  * `frontend/src/stores/interconsulta.ts`
  * `frontend/src/views/Interconsultas.vue`
  * `frontend/src/views/CentralMarcacao.vue`
  * `openspec/specs/encaminhamento-digital/spec.md`
  * `openspec/specs/visualizacao-central-marcacao/spec.md`

### LGPD e Trilhas de Auditoria
- O número de telefone celular/fixo do paciente é um dado de identificação pessoal e deve ser armazenado com criptografia simétrica AES-256 (Fernet) no banco de dados local da aplicação, assim como o PREP.
- A descriptografia só ocorre ao carregar os dados para visualização na Central de Marcação (por operadores autorizados) ou na exportação de KPIs pelo administrador, cujos acessos são registrados na trilha de auditoria.

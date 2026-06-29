## Design

### 1. Database Schema
- Adição da coluna `motivo_negacao` (VARCHAR, nullable) na tabela `interconsulta_pedidos`.
- Atualização do hook de lifespan em `src/main.py` para alterar e injetar a coluna nas tabelas do SQLite automaticamente no startup.

### 2. Layered Data Flow
- **SQL Templates:** Inserção de `motivo_negacao` no query template `inserir_pedido.sql` e retorno na query `listar_pedidos.sql`.
- **Provider:** Armazenamento e leitura de `motivo_negacao` em `InterconsultaPostgresProvider` and `InterconsultaMockProvider`.
- **Controller:** Ajuste da lógica em `InterconsultaController.solicitar_interconsulta` para setar `status = "ERRO"` e `motivo_negacao = "Não é papel do HC"` caso a gravidade seja `VERDE`.
- **Router:** Exposição do campo `motivo_negacao` na resposta Pydantic `InterconsultaResponse`.

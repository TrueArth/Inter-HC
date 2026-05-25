## 1. Banco de Dados e Modelagem (SQLAlchemy + SQL Nativos)

- [x] 1.1 Criar o modelo `InterconsultaPedido` em `src/models/interconsulta.py` contendo as colunas de negócio, `paciente_cns` e a coluna `deleted_at` para o Soft Delete.
- [x] 1.2 Gerar o arquivo de migração do banco usando Alembic (autogenerate) e aplicar.
- [x] 1.3 Criar o arquivo `src/providers/sql/interconsulta/inserir_pedido.sql` contendo o `INSERT` com instrução `RETURNING`.
- [x] 1.4 Criar o arquivo `src/providers/sql/interconsulta/soft_delete_pedido.sql` executando o update de `deleted_at`.
- [x] 1.5 Criar o arquivo `src/providers/sql/interconsulta/listar_pedidos.sql` para leitura das interconsultas, filtrando os registros ativos.
- [x] 1.6 Criar testes de repositório assegurando que o Soft Delete está operacional e AES-256 (via banco ou código) opera corretamente nos dados de CNS.

## 2. Camada Provider (Acesso a Dados)

- [x] 2.1 Criar a interface `InterconsultaProviderInterface` em `src/providers/interfaces/interconsulta_provider_interface.py`.
- [x] 2.2 Implementar a classe `InterconsultaPostgresProvider` em `src/providers/implementations/interconsulta_postgres_provider.py` obedecendo à interface.
- [x] 2.3 Atualizar o arquivo de injeção de dependências (`src/dependencies.py`) para exportar a factory/getter do provider de interconsulta.
- [x] 2.4 Criar testes unitários (ex: `tests/providers/test_interconsulta_provider.py`) usando pytest para garantir a invocação correta das SQLs e o comportamento de Soft Delete.

## 3. Mensageria Assíncrona (Message Broker)

- [x] 3.1 Instalar e configurar dependências de fila assíncrona (ex: `Celery` ou usar de modo nativo via `BackgroundTasks` caso em dev) no backend.
- [x] 3.2 Criar um worker job em `src/workers/central_marcacao_worker.py` (ou em `helpers/`) que simulará o envio do payload ao AGHU com bloco de `try/except` para lidar com Retry/Fallback (HTTP 503/500).

## 4. Motor de Regras e Camada Controller

- [x] 4.1 Criar a lógica do Motor de Regras da gravidade clínica (em um service auxiliar `RiskEngineService` ou no Controller) cruzando o array de sintomas.
- [x] 4.2 Criar a classe `InterconsultaController` em `src/controllers/interconsulta_controller.py` que receberá o payload, fará a chamada ao motor de regras (definindo Vermelho/Amarelo/Verde) e em seguida chamará o `provider.salvar()`.
- [x] 4.3 Configurar o Controller para publicar a mensagem no Message Broker logo após a persistência segura no BD.
- [x] 4.4 Escrever testes unitários (`tests/controllers/test_interconsulta_controller.py`) cobrindo 100% dos caminhos lógicos do cálculo de risco e despachos de mensageria.

## 5. Camada Router e API

- [x] 5.1 Criar as definições e schemas do Pydantic (`InterconsultaCreate`, `InterconsultaResponse`) em `src/routers/interconsulta.py`.
- [x] 5.2 Implementar os endpoints (POST para criar interconsulta, GET para listar) utilizando `Depends` para injetar o Provider e instanciar o Controller.
- [x] 5.3 Registrar o novo `interconsulta.router` no aplicativo FastAPI em `src/main.py`.
- [x] 5.4 Elaborar os testes de integração (`tests/routers/test_interconsulta_router.py`) verificando se um payload HTTP completo atravessa o Motor de Risco e salva no banco de testes.

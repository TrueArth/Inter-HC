"""
Testes de Integração — Router de Interconsulta (tarefa 5.4)

Verifica que um payload HTTP completo percorre a pilha inteira:
  HTTP → Router → Controller → Motor de Risco → Provider → Banco em memória

Estratégia:
  - SQLite in-memory via aiosqlite para o banco da aplicação
  - Override de `get_interconsulta_provider` para injetar provider SQLite
  - Override de `get_current_user` para simular um token JWT válido
  - `httpx.AsyncClient` com `ASGITransport` para chamadas reais ao app
"""

import os
import pytest
import pytest_asyncio

# Variáveis de ambiente devem estar definidas ANTES de qualquer import do app.
os.environ.setdefault("SQLITE_DSN", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-key-integration")
os.environ.setdefault("AES_SECRET_KEY", "")  # crypto_helper gera uma chave efêmera se vazio
os.environ["INTERCONSULTA_PROVIDER_TYPE"] = "POSTGRES"


from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ────────────────────────────────────────────────────────────────
# Setup do banco de testes (SQLite in-memory)
# ────────────────────────────────────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


# ────────────────────────────────────────────────────────────────
# Importa o app DEPOIS de definir as variáveis de ambiente
# ────────────────────────────────────────────────────────────────
from src.main import app
from src.resources.database import Base
from src.models.interconsulta import InterconsultaPedido  # noqa: F401 — registra tabela no metadata
from src.dependencies import get_interconsulta_provider
from src.providers.implementations.interconsulta_postgres_provider import InterconsultaPostgresProvider
from src.routers.interconsulta import get_current_user


# ────────────────────────────────────────────────────────────────
# Provider de teste: usa SQLite in-memory e dialeto correto
# ────────────────────────────────────────────────────────────────
async def _get_sqlite_interconsulta_provider() -> InterconsultaPostgresProvider:
    """Fornece um provider com sessão SQLite e dialect explícito para os testes."""
    async with _TestSession() as session:
        yield InterconsultaPostgresProvider(session=session, dialect="sqlite")


# ────────────────────────────────────────────────────────────────
# Overrides de dependências do FastAPI
# ────────────────────────────────────────────────────────────────
def _mock_current_user():
    """Simula um token JWT decodificado válido com privilégios de teste."""
    return {
        "name": "medico_teste",
        "sub": "medico_teste",
        "groups": ["GLO-SEC-HCPE-SETISD", "Medicos", "Users"],
        "role": "admin"
    }


# A factory get_interconsulta_provider retorna uma função de dependência.
# Precisamos sobrescrever a função interna que ela retorna.
from src.dependencies import _get_interconsulta_postgres_provider


# ────────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Cria as tabelas SQLite antes dos testes e as remove depois."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def client():
    """AsyncClient com transporte ASGI — faz chamadas HTTP reais ao app FastAPI."""
    app.dependency_overrides[_get_interconsulta_postgres_provider] = _get_sqlite_interconsulta_provider
    app.dependency_overrides[get_current_user] = _mock_current_user
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ────────────────────────────────────────────────────────────────
# Payloads de teste com diferentes níveis de risco
# ────────────────────────────────────────────────────────────────
PAYLOAD_CRITICO = {
    "paciente_cns": "123456789012345",
    "medico_solicitante_crm": "54321-PE",
    "especialidade_id": 1,
    "sintomas_json": [{"id": 1, "nome": "Cegueira"}],  # id=1 → VERMELHO
}

PAYLOAD_MODERADO = {
    "paciente_cns": "999888777665544",
    "medico_solicitante_crm": "11111-PB",
    "especialidade_id": 2,
    "sintomas_json": [{"id": 5, "nome": "Febre alta"}],  # id=5 → AMARELO
}

PAYLOAD_BAIXO = {
    "paciente_cns": "111222333445566",
    "medico_solicitante_crm": "22222-RJ",
    "especialidade_id": 3,
    "sintomas_json": [{"id": 99, "nome": "Tosse leve"}],  # sem match → VERDE
}


# ────────────────────────────────────────────────────────────────
# Testes de Integração
# ────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_criar_interconsulta_retorna_201(client: AsyncClient):
    """POST /api/interconsultas/ deve retornar HTTP 201 com o pedido criado."""
    response = await client.post("/api/interconsultas/", json=PAYLOAD_CRITICO)

    assert response.status_code == 201, response.text
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["paciente_cns"] == PAYLOAD_CRITICO["paciente_cns"]
    # O CRM deve ser sobrescrito com o nome do usuário autenticado (mock JWT)
    assert data["medico_solicitante_crm"] == "medico_teste"
    assert data["especialidade_id"] == PAYLOAD_CRITICO["especialidade_id"]


@pytest.mark.asyncio
async def test_motor_de_risco_classifica_vermelho(client: AsyncClient):
    """Sintoma crítico (id=1) deve acionar classificação VERMELHO pelo Motor de Risco."""
    response = await client.post("/api/interconsultas/", json=PAYLOAD_CRITICO)
    assert response.status_code == 201, response.text
    assert response.json()["gravidade"] == "VERMELHO"


@pytest.mark.asyncio
async def test_motor_de_risco_classifica_amarelo(client: AsyncClient):
    """Sintoma moderado (id=5) deve acionar classificação AMARELO pelo Motor de Risco."""
    response = await client.post("/api/interconsultas/", json=PAYLOAD_MODERADO)
    assert response.status_code == 201, response.text
    assert response.json()["gravidade"] == "AMARELO"


@pytest.mark.asyncio
async def test_motor_de_risco_classifica_verde(client: AsyncClient):
    """Sintoma de baixo risco (id sem match) deve resultar em classificação VERDE."""
    response = await client.post("/api/interconsultas/", json=PAYLOAD_BAIXO)
    assert response.status_code == 201, response.text
    assert response.json()["gravidade"] == "VERDE"


@pytest.mark.asyncio
async def test_listar_interconsultas_contem_pedido_criado(client: AsyncClient):
    """GET /api/interconsultas/ deve retornar a interconsulta recém-criada."""
    # Cria um pedido
    post_resp = await client.post("/api/interconsultas/", json=PAYLOAD_MODERADO)
    assert post_resp.status_code == 201, post_resp.text
    criado_data = post_resp.json()
    criado_id = criado_data["id"]

    # Lista e verifica se o pedido aparece
    list_resp = await client.get("/api/interconsultas/")
    assert list_resp.status_code == 200, list_resp.text
    pedidos = list_resp.json()
    ids = [item["id"] for item in pedidos]
    assert criado_id in ids, f"Pedido {criado_id} não encontrado na listagem"

    # Verifica se os novos campos de score e dias na fila estão presentes e são numéricos
    pedido_retornado = next(p for p in pedidos if p["id"] == criado_id)
    assert "score_prioridade" in pedido_retornado
    assert "dias_na_fila" in pedido_retornado
    assert isinstance(pedido_retornado["score_prioridade"], (int, float))
    assert isinstance(pedido_retornado["dias_na_fila"], int)


@pytest.mark.asyncio
async def test_payload_incompleto_retorna_422(client: AsyncClient):
    """Payload sem campos obrigatórios deve retornar HTTP 422 (Unprocessable Entity)."""
    payload_invalido = {"paciente_cns": "123456789012345"}
    response = await client.post("/api/interconsultas/", json=payload_invalido)
    assert response.status_code == 422

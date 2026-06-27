import os
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text, update

# Define env variables before app imports
os.environ.setdefault("SQLITE_DSN", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-key-dynamic-risk")
os.environ["USER_PROVIDER_TYPE"] = "POSTGRES"
os.environ["INTERCONSULTA_PROVIDER_TYPE"] = "POSTGRES"

from src.main import app
from src.resources.database import Base, get_app_db_session
from src.models.especialidade import Especialidade
from src.models.sintoma import Sintoma
from src.models.regra_gravidade import RegraGravidade
from src.models.interconsulta import InterconsultaPedido
from src.dependencies import _get_interconsulta_postgres_provider
from src.providers.implementations.interconsulta_postgres_provider import InterconsultaPostgresProvider
from src.routers.interconsulta import get_current_user

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

async def _get_sqlite_interconsulta_provider() -> InterconsultaPostgresProvider:
    """Fornece o interconsulta provider configurado para SQLite."""
    async with _TestSession() as session:
        yield InterconsultaPostgresProvider(session=session, dialect="sqlite")

async def _get_test_db_session():
    """Fornece uma sessão do banco de teste para todas as dependências."""
    async with _TestSession() as session:
        yield session

# Mocks para o controle de roles nos testes
_mock_user_role = "medico"

def _mock_current_user():
    return {
        "name": "usuario_teste",
        "sub": "usuario_teste",
        "groups": ["GLO-SEC-HCPE-SETISD" if _mock_user_role == "admin" else "Reguladores" if _mock_user_role == "regulador" else "Medicos"],
        "role": _mock_user_role
    }

@pytest_asyncio.fixture(scope="module", autouse=True)
async def create_tables():
    """Cria o esquema do banco de dados na memória e semeia dados de teste."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Semeia especialidades, sintomas e regras dinâmicas de teste
    async with _TestSession() as session:
        # Especialidade Pneumologia
        esp = Especialidade(id=15, nome="Pneumologia")
        session.add(esp)
        
        # Sintoma com pontuação padrão 2
        sint = Sintoma(id=20, nome="Tosse Crônica", pontuacao=2)
        session.add(sint)
        
        await session.commit()
        
        # Regra de pontuação que define Tosse Crônica para Pneumologia como 10 (VERMELHO)
        rule = RegraGravidade(sintoma_id=20, especialidade_id=15, pontuacao=10)
        session.add(rule)
        
        await session.commit()
        
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture()
async def client():
    """Retorna um AsyncClient com as dependências do banco e usuário mockadas."""
    app.dependency_overrides[_get_interconsulta_postgres_provider] = _get_sqlite_interconsulta_provider
    app.dependency_overrides[get_app_db_session] = _get_test_db_session
    app.dependency_overrides[get_current_user] = _mock_current_user
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_dynamic_gravity_override_applied(client: AsyncClient):
    """Verifica se o motor de risco carrega e aplica a regra de override dinâmica do banco."""
    global _mock_user_role
    _mock_user_role = "medico"
    
    payload = {
        "paciente_prep": "12345678",
        "medico_solicitante_crm": "medico_teste",
        "especialidade_id": 15,
        "sintomas_json": [{"id": 20, "nome": "Tosse Crônica"}]
    }
    response = await client.post("/api/interconsultas/", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["gravidade"] == "VERMELHO", "Deve aplicar a regra de priorização dinâmica do banco"

@pytest.mark.asyncio
async def test_queue_filtering_consultation_date(client: AsyncClient):
    """Verifica se consultas agendadas há mais de 24h somem do regulador mas continuam no admin."""
    global _mock_user_role
    
    # 1. Cria um pedido
    _mock_user_role = "medico"
    payload = {
        "paciente_prep": "7700201",
        "medico_solicitante_crm": "medico_teste",
        "especialidade_id": 15,
        "sintomas_json": [{"id": 20, "nome": "Tosse Crônica"}]
    }
    res = await client.post("/api/interconsultas/", json=payload)
    assert res.status_code == 201
    pedido_id = res.json()["id"]
    
    # 2. Atualiza status para AGENDADO com consulta agendada para 2 dias atrás
    # Burla a validação da API atualizando diretamente no banco de dados para simular o estado
    async with _TestSession() as session:
        two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
        await session.execute(
            update(InterconsultaPedido)
            .where(InterconsultaPedido.id == pedido_id)
            .values(status="AGENDADO", data_consulta=two_days_ago)
        )
        await session.commit()
    
    # 3. Lista pedidos como regulador -> deve estar OCULTO (passou mais de 1 dia da data da consulta)
    _mock_user_role = "regulador"
    list_res = await client.get("/api/interconsultas/")
    assert list_res.status_code == 200
    pedidos = list_res.json()
    ids = [p["id"] for p in pedidos]
    assert pedido_id not in ids, "Deve ocultar consultas realizadas há mais de 1 dia para o regulador"
    
    # 4. Lista pedidos como admin -> deve estar VISÍVEL
    _mock_user_role = "admin"
    list_res_admin = await client.get("/api/interconsultas/")
    assert list_res_admin.status_code == 200
    pedidos_admin = list_res_admin.json()
    ids_admin = [p["id"] for p in pedidos_admin]
    assert pedido_id in ids_admin, "Admin deve continuar visualizando todas as consultas agendadas"

    # 5. Cria outro pedido agendado para o futuro (amanhã)
    _mock_user_role = "medico"
    payload_future = {
        "paciente_prep": "7700301",
        "medico_solicitante_crm": "medico_teste",
        "especialidade_id": 15,
        "sintomas_json": [{"id": 20, "nome": "Tosse Crônica"}]
    }
    res_future = await client.post("/api/interconsultas/", json=payload_future)
    assert res_future.status_code == 201
    pedido_future_id = res_future.json()["id"]
    
    _mock_user_role = "regulador"
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    update_future_res = await client.patch(
        f"/api/interconsultas/{pedido_future_id}/status",
        json={"status": "AGENDADO", "data_consulta": tomorrow}
    )
    assert update_future_res.status_code == 200

    # 6. Lista pedidos como regulador -> deve estar VISÍVEL
    list_res_future = await client.get("/api/interconsultas/")
    assert list_res_future.status_code == 200
    pedidos_future = list_res_future.json()
    ids_future = [p["id"] for p in pedidos_future]
    assert pedido_future_id in ids_future, "Regulador deve conseguir ver consultas futuras"

@pytest.mark.asyncio
async def test_api_blocks_past_consultation_date(client: AsyncClient):
    """Verifica se a API bloqueia o agendamento de consultas para datas no passado."""
    global _mock_user_role
    _mock_user_role = "medico"
    payload = {
        "paciente_prep": "7700401",
        "medico_solicitante_crm": "medico_teste",
        "especialidade_id": 15,
        "sintomas_json": [{"id": 20, "nome": "Tosse Crônica"}]
    }
    res = await client.post("/api/interconsultas/", json=payload)
    assert res.status_code == 201
    pedido_id = res.json()["id"]

    # Tenta agendar para ontem -> deve retornar 400 Bad Request
    _mock_user_role = "regulador"
    past_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    update_res = await client.patch(
        f"/api/interconsultas/{pedido_id}/status",
        json={"status": "AGENDADO", "data_consulta": past_date}
    )
    assert update_res.status_code == 400
    assert "Não é possível agendar uma consulta para uma data no passado." in update_res.json()["detail"]

@pytest.mark.asyncio
async def test_api_blocks_invalid_prep(client: AsyncClient):
    """Verifica se a API rejeita requisições com PREP inválido (letras ou comprimento incorreto)."""
    global _mock_user_role
    _mock_user_role = "medico"
    
    # 1. PREP com letras
    payload_alpha = {
        "paciente_prep": "1234567a",
        "medico_solicitante_crm": "medico_teste",
        "especialidade_id": 15,
        "sintomas_json": [{"id": 20, "nome": "Tosse Crônica"}]
    }
    res_alpha = await client.post("/api/interconsultas/", json=payload_alpha)
    assert res_alpha.status_code == 422
    assert "O número do PREP deve conter apenas dígitos numéricos." in res_alpha.text

    # 2. PREP muito curto
    payload_short = {
        "paciente_prep": "123456",
        "medico_solicitante_crm": "medico_teste",
        "especialidade_id": 15,
        "sintomas_json": [{"id": 20, "nome": "Tosse Crônica"}]
    }
    res_short = await client.post("/api/interconsultas/", json=payload_short)
    assert res_short.status_code == 422
    assert "O número do PREP deve conter entre 7 e 8 dígitos." in res_short.text


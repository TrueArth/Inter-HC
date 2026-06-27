import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SQLITE_DSN", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-key-profile-stats")
os.environ["USER_PROVIDER_TYPE"] = "POSTGRES"
os.environ["INTERCONSULTA_PROVIDER_TYPE"] = "POSTGRES"


from src.main import app
from src.resources.database import Base, get_app_db_session
from src.models.user import User  # Registers user table
from src.models.interconsulta import InterconsultaPedido  # Registers table
from src.dependencies import _get_user_postgres_provider, _get_interconsulta_postgres_provider
from src.providers.implementations.user_postgres_provider import UserPostgresProvider
from src.providers.implementations.interconsulta_postgres_provider import InterconsultaPostgresProvider
from src.auth.auth import auth_handler

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

async def _get_sqlite_user_provider() -> UserPostgresProvider:
    async with _TestSession() as session:
        yield UserPostgresProvider(session=session, dialect="sqlite")

async def _get_sqlite_interconsulta_provider() -> InterconsultaPostgresProvider:
    async with _TestSession() as session:
        yield InterconsultaPostgresProvider(session=session, dialect="sqlite")

async def _get_test_db_session():
    async with _TestSession() as session:
        yield session

# Helper mock users
def _mock_admin_user():
    return {"username": "admin_test", "role": "admin", "groups": ["GLO-SEC-HCPE-SETISD"]}

def _mock_regular_user():
    return {"username": "medico_test", "role": "medico", "groups": ["Medicos"]}

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture()
async def client():
    app.dependency_overrides[_get_user_postgres_provider] = _get_sqlite_user_provider
    app.dependency_overrides[_get_interconsulta_postgres_provider] = _get_sqlite_interconsulta_provider
    app.dependency_overrides[get_app_db_session] = _get_test_db_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient):
    app.dependency_overrides[auth_handler.decode_token] = _mock_regular_user
    
    # 1. Create a user first in our DB so we can update it
    async for provider in _get_sqlite_user_provider():
        from src.helpers.crypto_helper import hash_password
        await provider.inserir_usuario({
            "username": "medico_test",
            "hashed_password": hash_password("oldpassword"),
            "display_name": "Dr. House",
            "role": "medico",
            "email": "house@ufpe.br"
        })
        break

    # 2. Update profile
    payload = {
        "display_name": "Dr. Gregory House",
        "email": "gregory@ufpe.br",
        "password": "newsecretpassword"
    }
    response = await client.put("/api/users/profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Dr. Gregory House"
    assert data["email"] == "gregory@ufpe.br"

@pytest.mark.asyncio
async def test_get_statistics_admin_only(client: AsyncClient):
    # 1. Regular user gets 403
    app.dependency_overrides[auth_handler.decode_token] = _mock_regular_user
    response = await client.get("/api/admin/statistics")
    assert response.status_code == 403

    # 2. Admin user gets 200
    app.dependency_overrides[auth_handler.decode_token] = _mock_admin_user
    response = await client.get("/api/admin/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "top_specialty" in data
    assert "specialties_distribution" in data
    assert "top_doctors" in data
    assert "inappropriate_doctors" in data
    # Novas chaves
    assert "total_interconsultas" in data
    assert "tempo_medio_atendimento_segundos" in data
    assert "tempo_medio_atendimento_formatado" in data
    assert "especialidades_mais_pendencias" in data


@pytest.mark.asyncio
async def test_export_statistics_excel_admin_only(client: AsyncClient):
    # 1. Regular user gets 403
    app.dependency_overrides[auth_handler.decode_token] = _mock_regular_user
    response = await client.get("/api/admin/statistics/export")
    assert response.status_code == 403

    # 2. Admin user gets 200 and Excel stream
    app.dependency_overrides[auth_handler.decode_token] = _mock_admin_user
    response = await client.get("/api/admin/statistics/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "Content-Disposition" in response.headers
    assert "attachment" in response.headers["Content-Disposition"]
    assert len(response.content) > 0

    # 3. Verify worksheets and contents
    import io
    import pandas as pd
    excel_file = io.BytesIO(response.content)
    xls = pd.ExcelFile(excel_file)
    sheets = xls.sheet_names
    assert "Indicadores Gerais" in sheets
    assert "Fila Reguladora" in sheets
    assert "Volume por Especialidade" in sheets
    assert "Pendencias por Especialidade" in sheets
    assert "Medicos Mais Solicitantes" in sheets
    assert "Casos Indevidos por Medico" in sheets
    assert "Controle de Usuarios" in sheets
    assert "Catalogo Especialidades" in sheets
    assert "Catalogo Sintomas" in sheets

    df_geral = pd.read_excel(excel_file, sheet_name="Indicadores Gerais")
    kpis = df_geral["Indicador"].tolist()
    assert "Total de Interconsultas" in kpis
    assert "Tempo Médio de Atendimento da Marcação" in kpis
    assert "Especialidade Mais Solicitada (Nome)" in kpis
    assert "Total de Casos Indevidos (Verde)" in kpis

    df_esp = pd.read_excel(excel_file, sheet_name="Volume por Especialidade")
    assert "Especialidade" in df_esp.columns
    assert "Total de Solicitações" in df_esp.columns

    df_docs = pd.read_excel(excel_file, sheet_name="Medicos Mais Solicitantes")
    assert "Médico Solicitante" in df_docs.columns
    assert "Volume de Solicitações" in df_docs.columns

    df_users = pd.read_excel(excel_file, sheet_name="Controle de Usuarios")
    assert "ID Usuário" in df_users.columns
    assert "Nome Exibido" in df_users.columns

    df_cat_esp = pd.read_excel(excel_file, sheet_name="Catalogo Especialidades")
    assert "ID Especialidade" in df_cat_esp.columns
    assert "Nome da Especialidade" in df_cat_esp.columns

    df_cat_sint = pd.read_excel(excel_file, sheet_name="Catalogo Sintomas")
    assert "ID Sintoma" in df_cat_sint.columns
    assert "Nome do Sintoma" in df_cat_sint.columns



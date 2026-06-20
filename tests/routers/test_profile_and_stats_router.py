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
from src.resources.database import Base
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

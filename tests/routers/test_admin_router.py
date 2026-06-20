import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SQLITE_DSN", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-key-admin")

from src.main import app
from src.resources.database import Base
from src.models.user import User  # Registers user table
from src.dependencies import get_user_provider
from src.providers.implementations.user_postgres_provider import UserPostgresProvider
from src.routers.admin import verify_admin_group
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

# Override dependencies
from src.dependencies import _get_user_postgres_provider

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
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_admin_data_access_denied_for_regular_user(client: AsyncClient):
    # Set override for regular user
    app.dependency_overrides[auth_handler.decode_token] = _mock_regular_user
    response = await client.get("/api/admin-only-data")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_data_access_allowed_for_admin_user(client: AsyncClient):
    # Set override for admin user
    app.dependency_overrides[auth_handler.decode_token] = _mock_admin_user
    response = await client.get("/api/admin-only-data")
    assert response.status_code == 200
    assert response.json()["message"] == "This is highly confidential admin data!"

@pytest.mark.asyncio
async def test_user_crud_operations(client: AsyncClient):
    app.dependency_overrides[auth_handler.decode_token] = _mock_admin_user
    
    # 1. Create a user
    new_user_payload = {
        "username": "new_medico",
        "password": "secretpassword",
        "display_name": "Dr. House",
        "role": "medico",
        "email": "house@ufpe.br"
    }
    response = await client.post("/api/admin/users", json=new_user_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_medico"
    assert data["display_name"] == "Dr. House"
    assert data["role"] == "medico"
    assert "password" not in data
    user_id = data["id"]

    # 2. List users
    response = await client.get("/api/admin/users")
    assert response.status_code == 200
    users = response.json()
    usernames = [u["username"] for u in users]
    assert "new_medico" in usernames

    # 3. Update user
    update_payload = {
        "display_name": "Dr. Gregory House",
        "email": "gregory@ufpe.br"
    }
    response = await client.put(f"/api/admin/users/{user_id}", json=update_payload)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["display_name"] == "Dr. Gregory House"
    assert updated_data["email"] == "gregory@ufpe.br"

    # 4. Delete user
    response = await client.delete(f"/api/admin/users/{user_id}")
    assert response.status_code == 200
    
    # Verify no longer listed
    response = await client.get("/api/admin/users")
    users = response.json()
    ids = [u["id"] for u in users]
    assert user_id not in ids

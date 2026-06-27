import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.resources.database import Base
from src.models.interconsulta import InterconsultaPedido  # noqa: F401 — registra tabela no metadata
from src.providers.implementations.interconsulta_postgres_provider import InterconsultaPostgresProvider
from src.helpers.crypto_helper import encrypt_data

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_inserir_listar_inativar_pedido(db_session: AsyncSession):
    provider = InterconsultaPostgresProvider(session=db_session, dialect="sqlite")
    
    # 1. Inserir pedido
    novo_pedido = {
        "paciente_prep": "7700201",
        "medico_solicitante_crm": "54321-PE",
        "especialidade_id": 2,
        "sintomas_json": [{"id": 5, "nome": "Febre"}],
        "gravidade": "AMARELO",
        "status": "PENDENTE"
    }
    
    criado = await provider.inserir_pedido(novo_pedido)
    assert criado["id"] is not None
    # Deve retornar desencriptado conforme a implementação
    assert criado["paciente_prep"] == "7700201"
    
    # 2. Listar pedidos
    pedidos = await provider.listar_pedidos_ativos()
    assert len(pedidos) == 1
    assert pedidos[0]["id"] == criado["id"]
    assert pedidos[0]["paciente_prep"] == "7700201"
    
    # 3. Soft Delete
    sucesso = await provider.inativar_pedido(criado["id"])
    assert sucesso is True
    
    # 4. Verificar listagem novamente
    pedidos_ativos = await provider.listar_pedidos_ativos()
    assert len(pedidos_ativos) == 0

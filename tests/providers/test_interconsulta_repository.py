import pytest
from datetime import datetime, timezone
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.resources.database import Base
from src.models.interconsulta import InterconsultaPedido
from src.helpers.crypto_helper import encrypt_data, decrypt_data

# In-memory SQLite for fast testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_interconsulta_soft_delete(db_session: AsyncSession):
    # Cria pedido mock
    pedido = InterconsultaPedido(
        paciente_prep=encrypt_data("10000016"),
        medico_solicitante_crm="12345-PE",
        especialidade_id=1,
        sintomas_json=[{"id": 1, "nome": "Dor Torácica"}],
        gravidade="VERMELHO"
    )
    db_session.add(pedido)
    await db_session.commit()
    await db_session.refresh(pedido)

    assert pedido.id is not None
    assert pedido.deleted_at is None

    # Aplica Soft Delete
    pedido.deleted_at = datetime.now(timezone.utc)
    db_session.add(pedido)
    await db_session.commit()
    await db_session.refresh(pedido)

    assert pedido.deleted_at is not None

@pytest.mark.asyncio
async def test_interconsulta_aes_encryption(db_session: AsyncSession):
    original_prep = "10000016"
    encrypted_prep = encrypt_data(original_prep)
    
    # O valor criptografado deve ser diferente do original
    assert encrypted_prep != original_prep
    
    pedido = InterconsultaPedido(
        paciente_prep=encrypted_prep,
        medico_solicitante_crm="12345-PE",
        especialidade_id=1,
        sintomas_json=[{"id": 1, "nome": "Dor Torácica"}],
        gravidade="VERMELHO"
    )
    db_session.add(pedido)
    await db_session.commit()
    await db_session.refresh(pedido)

    # Verifica se ao puxar do banco, a descriptografia funciona
    prep_retornado = decrypt_data(pedido.paciente_prep)
    assert prep_retornado == original_prep

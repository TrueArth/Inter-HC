import os
from typing import Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from .providers.implementations.paciente_postgres_provider import PacientePostgresProvider
from .providers.implementations.paciente_csv_provider import PacienteCsvProvider
from .resources.database import get_aghu_db_session
from .providers.implementations.leito_postgres_provider import LeitoPostgresProvider
from .resources.database import get_aghu_db_session

def get_leito_provider(
    session: AsyncSession = Depends(get_aghu_db_session)
) -> LeitoPostgresProvider:
    return LeitoPostgresProvider(session=session)
# 1. Funções "getter" simples e independentes (privadas por convenção)
def _get_paciente_postgres_provider(
    session: AsyncSession = Depends(get_aghu_db_session)
) -> PacienteProviderInterface:
    return PacientePostgresProvider(session=session)

def _get_paciente_csv_provider() -> PacienteProviderInterface:
    csv_path = os.getenv("PACIENTE_CSV_PATH", "data/pacientes.csv")
    return PacienteCsvProvider(csv_path=csv_path)

# 2. A FÁBRICA: A única função que o roteador vai conhecer.
def get_paciente_provider(strategy: str) -> Callable[..., PacienteProviderInterface]:
    """
    Esta é uma fábrica. Baseado na string 'strategy', ela não retorna o provedor,
    mas sim a FUNÇÃO DE DEPENDÊNCIA correta que o FastAPI deve usar.
    """
    if strategy.upper() == "POSTGRES":
        return _get_paciente_postgres_provider
    elif strategy.upper() == "CSV":
        return _get_paciente_csv_provider
    else:
        raise ValueError(f"Estratégia de provedor desconhecida: {strategy}")

# --- Interconsulta Provider Factory ---
from .providers.interfaces.interconsulta_provider_interface import InterconsultaProviderInterface
from .providers.implementations.interconsulta_postgres_provider import InterconsultaPostgresProvider
from .providers.implementations.interconsulta_mock_provider import InterconsultaMockProvider
from .resources.database import get_app_db_session

def _get_interconsulta_postgres_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> InterconsultaProviderInterface:
    # Detects the engine dialect (sqlite vs postgresql) to pass correct strategy
    dialect = session.bind.dialect.name if session.bind else "postgresql"
    return InterconsultaPostgresProvider(session=session, dialect=dialect)

def _get_interconsulta_mock_provider() -> InterconsultaProviderInterface:
    return InterconsultaMockProvider()

def get_interconsulta_provider(strategy: str = "POSTGRES") -> Callable[..., InterconsultaProviderInterface]:
    # Check if there is an environment variable override (e.g. for development)
    env_strategy = os.getenv("INTERCONSULTA_PROVIDER_TYPE", None)
    selected_strategy = env_strategy if env_strategy is not None else strategy
    
    if selected_strategy.upper() == "POSTGRES":
        return _get_interconsulta_postgres_provider
    elif selected_strategy.upper() == "MOCK":
        return _get_interconsulta_mock_provider
    else:
        raise ValueError(f"Estratégia de interconsulta desconhecida: {selected_strategy}")

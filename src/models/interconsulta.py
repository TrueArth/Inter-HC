from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from datetime import datetime, timezone
import json

from ..resources.database import Base

class InterconsultaPedido(Base):
    __tablename__ = "interconsulta_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    paciente_cns = Column(String, index=True, nullable=False) # Armazenará o CNS (idealmente criptografado)
    medico_solicitante_crm = Column(String, nullable=False)
    especialidade_id = Column(Integer, nullable=False)
    
    # Usaremos JSON genérico compatível com SQLite e Postgres
    sintomas_json = Column(JSON, nullable=False, default=list) 
    
    gravidade = Column(String, nullable=False) # VERMELHO, AMARELO, VERDE
    status = Column(String, nullable=False, default="PENDENTE") # PENDENTE, ENFILEIRADO, AGENDADO, ERRO
    marcado_por = Column(String, nullable=True) # Identifica o marcador que agendou a consulta
    
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = Column(DateTime, nullable=True) # Coluna essencial para o Soft Delete (LGPD)

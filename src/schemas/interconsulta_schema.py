from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Sintoma(BaseModel):
    id: int
    nome: str

class InterconsultaCreate(BaseModel):
    paciente_cns: str = Field(..., description="CNS do paciente (será encriptado via AES-256 no banco)")
    medico_solicitante_crm: str = Field(..., description="CRM do médico logado solicitante")
    especialidade_id: int = Field(..., description="ID da especialidade desejada no AGHU")
    sintomas_json: List[Sintoma] = Field(default_factory=list, description="Lista de sintomas para análise do Motor de Risco")

class InterconsultaResponse(BaseModel):
    id: int
    paciente_cns: str
    medico_solicitante_crm: str
    especialidade_id: int
    gravidade: str
    status: str
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    score_prioridade: Optional[float] = None
    dias_na_fila: Optional[int] = None

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str = Field(..., description="Novo status do pedido (ex: AGENDADO, ERRO)")
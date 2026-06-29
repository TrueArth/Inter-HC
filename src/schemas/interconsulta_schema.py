from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class Sintoma(BaseModel):
    id: int
    nome: str

class InterconsultaCreate(BaseModel):
    paciente_prep: str = Field(..., description="PREP do paciente (será encriptado via AES-256 no banco)")
    paciente_contato: Optional[str] = Field(None, description="Contato do paciente no formato (dd) xxxxx-xxxx")
    medico_solicitante_crm: str = Field(..., description="CRM do médico logado solicitante")
    especialidade_id: int = Field(..., description="ID da especialidade desejada no AGHU")
    sintomas_json: List[Sintoma] = Field(default_factory=list, description="Lista de sintomas para análise do Motor de Risco")

    @field_validator("paciente_prep")
    @classmethod
    def validate_prep_format(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean.isdigit():
            raise ValueError("O número do PREP deve conter apenas dígitos numéricos.")
        if not (7 <= len(v_clean) <= 8):
            raise ValueError("O número do PREP deve conter entre 7 e 8 dígitos.")
        return v_clean

    @field_validator("paciente_contato")
    @classmethod
    def validate_contato_format(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v_clean = v.strip()
        import re
        regex = r"^\(\d{2}\)\s?\d{4,5}-\s?\d{4}$"
        if not re.match(regex, v_clean):
            raise ValueError("O número de contato do paciente deve estar no formato (dd) xxxxx-xxxx ou (dd) xxxx-xxxx.")
        return v_clean

class InterconsultaResponse(BaseModel):
    id: int
    paciente_prep: str
    paciente_nome: Optional[str] = None
    paciente_contato: Optional[str] = None
    medico_solicitante_crm: str
    especialidade_id: int
    sintomas_json: List[Sintoma] = Field(default_factory=list)
    gravidade: str
    status: str
    marcado_por: Optional[str] = None
    data_consulta: Optional[datetime] = None
    motivo_negacao: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    score_prioridade: Optional[float] = None
    dias_na_fila: Optional[int] = None

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str = Field(..., description="Novo status do pedido (ex: AGENDADO, ERRO)")
    data_consulta: Optional[datetime] = Field(None, description="Data/Hora confirmada da consulta")
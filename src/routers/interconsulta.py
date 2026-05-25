from fastapi import APIRouter, Depends, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.controllers.interconsulta_controller import InterconsultaController
from src.providers.interfaces.interconsulta_provider_interface import InterconsultaProviderInterface
from src.dependencies import get_interconsulta_provider
from src.auth.auth import auth_handler

get_current_user = auth_handler.decode_token

router = APIRouter(
    prefix="/api/interconsultas",
    tags=["Interconsultas"],
    responses={404: {"description": "Não encontrado"}},
)

# --- Schemas (Pydantic) ---

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

# --- Endpoints ---

@router.post("/", response_model=InterconsultaResponse, status_code=status.HTTP_201_CREATED)
async def criar_interconsulta(
    payload: InterconsultaCreate,
    background_tasks: BackgroundTasks,
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    current_user: dict = Depends(get_current_user)  # Exige token JWT
):
    """
    Submete um novo pedido de interconsulta.
    Aciona o Motor de Regras e enfileira no Message Broker.
    """
    # Sobrescreve o CRM do payload com o usuário logado para segurança
    dados = payload.dict()
    dados["medico_solicitante_crm"] = current_user.get("name", dados["medico_solicitante_crm"])
    
    pedido = await InterconsultaController.solicitar_interconsulta(
        payload=dados,
        provider=provider,
        background_tasks=background_tasks
    )
    return pedido

@router.get("/", response_model=List[InterconsultaResponse])
async def listar_interconsultas(
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os pedidos ativos (Soft Delete out), ordenados por prioridade clínica.
    """
    return await InterconsultaController.listar_pedidos(provider)

@router.delete("/{pedido_id}")
async def inativar_interconsulta(
    pedido_id: int,
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    current_user: dict = Depends(get_current_user)
):
    """
    Realiza o Soft Delete em um pedido de interconsulta (obrigatório LGPD).
    """
    return await InterconsultaController.cancelar_pedido(pedido_id, provider)

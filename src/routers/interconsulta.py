import os
from src.schemas.interconsulta_schema import InterconsultaCreate, InterconsultaResponse, StatusUpdate
from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.services.queue_optimizer_service import QueueOptimizerService

from src.controllers.interconsulta_controller import InterconsultaController
from src.providers.interfaces.interconsulta_provider_interface import InterconsultaProviderInterface
from src.dependencies import get_interconsulta_provider, get_catalogo_provider, get_paciente_provider
from src.auth.auth import auth_handler


get_current_user = auth_handler.decode_token

router = APIRouter(
    prefix="/api/interconsultas",
    tags=["Interconsultas"],
    responses={404: {"description": "Não encontrado"}},
)

# --- Schemas (Pydantic) ---

# --- Endpoints ---

async def verify_medico_user(current_user: dict = Depends(get_current_user)):
    role = current_user.get("role")
    if role:
        if role not in ["medico", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acesso negado: Apenas médicos ou administradores possuem acesso a esta operação."
            )
    else:
        groups = current_user.get("groups", [])
        ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"
        if "Medicos" not in groups and ADMIN_GROUP not in groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acesso negado: Apenas médicos ou administradores possuem acesso a esta operação."
            )
    return current_user

@router.post("/", response_model=InterconsultaResponse, status_code=status.HTTP_201_CREATED)
async def criar_interconsulta(
    payload: InterconsultaCreate,
    background_tasks: BackgroundTasks,
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    catalogo_provider = Depends(get_catalogo_provider()),
    paciente_provider = Depends(get_paciente_provider(os.getenv("PACIENTE_PROVIDER_TYPE", "CSV"))),
    current_user: dict = Depends(verify_medico_user)  # Exige token JWT de médico/admin
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
        catalogo_provider=catalogo_provider,
        paciente_provider=paciente_provider,
        background_tasks=background_tasks
    )
    return pedido


async def verify_regulator_user(current_user: dict = Depends(get_current_user)):
    ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"
    role = current_user.get("role")
    if role:
        if role not in ["regulador", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acesso negado: Apenas a equipe de regulação da Central de Marcação possui acesso a esta operação."
            )
    else:
        groups = current_user.get("groups", [])
        if ADMIN_GROUP not in groups and "Reguladores" not in groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acesso negado: Apenas a equipe de regulação da Central de Marcação possui acesso a esta operação."
            )
    return current_user

@router.get("/", response_model=List[InterconsultaResponse])
async def listar_interconsultas(
    especialidade_id: Optional[int] = None,
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    current_user: dict = Depends(verify_regulator_user) # Exige regulador ou admin
):
    """
    Lista todos os pedidos ativos (Soft Delete out), ordenados por prioridade clínica.
    """
    return await InterconsultaController.listar_pedidos(provider, current_user, especialidade_id)

@router.delete("/{pedido_id}")
async def inativar_interconsulta(
    pedido_id: int,
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    current_user: dict = Depends(verify_medico_user) # Apenas médico/admin
):
    """
    Realiza o Soft Delete em um pedido de interconsulta (obrigatório LGPD).
    """
    return await InterconsultaController.cancelar_pedido(pedido_id, provider)

@router.patch("/{pedido_id}/status")
async def atualizar_status_pedido(
    pedido_id: int,
    payload: StatusUpdate,
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    current_user: dict = Depends(verify_regulator_user)
):
    """
    Atualiza o status de uma interconsulta. Apenas para reguladores/admin.
    """
    username = current_user.get("username") or current_user.get("sub") or "regulador"
    return await InterconsultaController.atualizar_status(pedido_id, payload.status, provider, marcado_por=username, data_consulta=payload.data_consulta)

@router.post("/{pedido_id}/retry")
async def reprocessar_pedido(
    pedido_id: int,
    background_tasks: BackgroundTasks,
    provider: InterconsultaProviderInterface = Depends(get_interconsulta_provider(strategy="POSTGRES")),
    current_user: dict = Depends(verify_regulator_user)
):
    """
    Reprocessa o envio de uma interconsulta que falhou. Apenas para reguladores/admin.
    """
    return await InterconsultaController.reprocessar_envio(pedido_id, provider, background_tasks)

@router.get("/sintomas")
async def listar_sintomas(
    provider = Depends(get_catalogo_provider()),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os sintomas ativos do catálogo.
    """
    from src.controllers.catalogo_controller import CatalogoController
    return await CatalogoController.listar_sintomas(provider)

@router.get("/especialidades/{especialidade_id}/sintomas")
async def listar_sintomas_por_especialidade(
    especialidade_id: int,
    provider = Depends(get_catalogo_provider()),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os sintomas ativos associados a uma especialidade específica.
    """
    from src.controllers.catalogo_controller import CatalogoController
    return await CatalogoController.listar_sintomas_por_especialidade(especialidade_id, provider)

@router.get("/especialidades")
async def listar_especialidades(
    provider = Depends(get_catalogo_provider()),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todas as especialidades ativas do catálogo.
    """
    from src.controllers.catalogo_controller import CatalogoController
    return await CatalogoController.listar_especialidades(provider)

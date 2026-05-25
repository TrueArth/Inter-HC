from fastapi import APIRouter, Depends
from typing import List
from ..auth.auth import auth_handler
from ..controllers import leito_controller
from ..dependencies import get_leito_provider
from ..providers.implementations.leito_postgres_provider import LeitoPostgresProvider

router = APIRouter(
    prefix="/api/leitos",
    tags=["Leitos"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("/setor/{setor_id}", response_model=List[dict])
async def listar_leitos(
    setor_id: int,
    provider: LeitoPostgresProvider = Depends(get_leito_provider)
):
    return await leito_controller.listar_leitos_setor(setor_id, provider)
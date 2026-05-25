from typing import List, Dict, Any
from fastapi import HTTPException
from ..providers.implementations.leito_postgres_provider import LeitoPostgresProvider

async def listar_leitos_setor(
    setor_id: int, 
    provider: LeitoPostgresProvider
) -> List[Dict[str, Any]]:
    if setor_id <= 0:
         raise HTTPException(status_code=400, detail="Setor inválido.")
    return await provider.listar_por_setor(setor_id)
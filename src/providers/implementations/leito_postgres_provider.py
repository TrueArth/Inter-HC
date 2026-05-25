import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

def get_sql_query(file_path: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(base_dir, '..', 'sql', file_path)
    with open(sql_file_path, 'r') as f:
        return f.read()

class LeitoPostgresProvider:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_por_setor(self, setor_id: int) -> List[Dict[str, Any]]:
        query_string = get_sql_query("leito/listar_leitos.sql")
        query = text(query_string)
        
        result = await self.session.execute(query, {"setor_id": setor_id})
        return [dict(row) for row in result.mappings().all()]
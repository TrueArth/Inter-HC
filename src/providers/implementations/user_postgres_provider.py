import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from ..interfaces.user_provider_interface import UserProviderInterface
from src.helpers.sql_helper import create_query, read_sql_file

def _get_sql_path(filename: str) -> str:
    """Retorna o caminho absoluto para um arquivo SQL do módulo user."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, '..', '..', 'providers', 'sql', 'user', filename)

class UserPostgresProvider(UserProviderInterface):
    """
    Provedor de dados para Usuários usando SQL nativo.
    """

    def __init__(self, session: AsyncSession, dialect: str = "postgresql"):
        self.session = session
        self._dialect = dialect.lower()

    async def inserir_usuario(self, user_data: dict) -> dict:
        params = dict(user_data)
        
        if self._dialect == "sqlite":
            sql_template = read_sql_file(_get_sql_path("inserir_usuario.sql"))
            sql_clean = sql_template.split("RETURNING")[0].rstrip().rstrip(";")
            query_str = create_query(sql_clean, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            new_id = result.lastrowid
            
            select_sql = text(
                "SELECT id, username, display_name, role, email, created_at, updated_at "
                "FROM users WHERE id = :id"
            )
            res = await self.session.execute(select_sql, {"id": new_id})
            row = res.mappings().first()
            return dict(row) if row else {}
        else:
            sql_template = read_sql_file(_get_sql_path("inserir_usuario.sql"))
            query_str = create_query(sql_template, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            row = result.mappings().first()
            return dict(row) if row else {}

    async def listar_usuarios(self) -> List[Dict[str, Any]]:
        sql_template = read_sql_file(_get_sql_path("listar_usuarios.sql"))
        result = await self.session.execute(text(sql_template))
        rows = result.mappings().all()
        return [dict(r) for r in rows]

    async def atualizar_usuario(self, user_id: int, user_data: dict) -> dict:
        params = dict(user_data)
        params["id"] = user_id
        params.setdefault("display_name", None)
        params.setdefault("role", None)
        params.setdefault("email", None)
        params.setdefault("hashed_password", None)
        
        if self._dialect == "sqlite":
            sql_template = read_sql_file(_get_sql_path("atualizar_usuario.sql"))
            sql_clean = sql_template.split("RETURNING")[0].rstrip().rstrip(";")
            query_str = create_query(sql_clean, params)
            await self.session.execute(text(query_str))
            await self.session.commit()
            
            select_sql = text(
                "SELECT id, username, display_name, role, email, created_at, updated_at "
                "FROM users WHERE id = :id"
            )
            res = await self.session.execute(select_sql, {"id": user_id})
            row = res.mappings().first()
            return dict(row) if row else {}
        else:
            sql_template = read_sql_file(_get_sql_path("atualizar_usuario.sql"))
            query_str = create_query(sql_template, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            row = result.mappings().first()
            return dict(row) if row else {}

    async def inativar_usuario(self, user_id: int) -> bool:
        params = {"id": user_id}
        if self._dialect == "sqlite":
            sql_template = read_sql_file(_get_sql_path("deletar_usuario.sql"))
            sql_clean = sql_template.split("RETURNING")[0].rstrip().rstrip(";")
            query_str = create_query(sql_clean, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            return result.rowcount > 0
        else:
            sql_template = read_sql_file(_get_sql_path("deletar_usuario.sql"))
            query_str = create_query(sql_template, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            row = result.mappings().first()
            return row is not None

    async def buscar_usuario_por_username(self, username: str) -> Optional[dict]:
        select_sql = text(
            "SELECT id, username, hashed_password, display_name, role, email, created_at, updated_at "
            "FROM users WHERE username = :username AND deleted_at IS NULL"
        )
        result = await self.session.execute(select_sql, {"username": username})
        row = result.mappings().first()
        return dict(row) if row else None

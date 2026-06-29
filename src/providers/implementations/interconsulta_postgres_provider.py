import os
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from ..interfaces.interconsulta_provider_interface import InterconsultaProviderInterface
from src.helpers.crypto_helper import encrypt_data, decrypt_data
from src.helpers.sql_helper import create_query, read_sql_file


def _get_sql_path(filename: str) -> str:
    """Retorna o caminho absoluto para um arquivo SQL do módulo interconsulta."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, '..', 'sql', 'interconsulta', filename)


class InterconsultaPostgresProvider(InterconsultaProviderInterface):
    """
    Provedor de dados para Interconsulta usando PostgreSQL (ou SQLite em testes).

    Executa SQLs nativos com substituição de placeholders via sql_helper.
    Aplica criptografia AES-256 no campo `paciente_prep` antes de persistir.
    """

    def __init__(self, session: AsyncSession, dialect: str = "postgresql"):
        self.session = session
        # Permite injetar o dialeto para compatibilidade com SQLite nos testes
        self._dialect = dialect.lower()

    async def inserir_pedido(self, pedido_data: dict) -> dict:
        """
        Insere um pedido de interconsulta e retorna o registro criado.

        Criptografa `paciente_prep` antes da persistência.
        Retorna com o PREP descriptografado para uso imediato pela API.
        """
        prep_original = pedido_data.get("paciente_prep", "")
        contato_original = pedido_data.get("paciente_contato")

        # Prepara cópia com dados transformados para o SQL
        params = dict(pedido_data)
        params["paciente_prep"] = encrypt_data(prep_original)
        params["paciente_contato"] = encrypt_data(contato_original) if contato_original else None
        params.setdefault("marcado_por", None)
        params.setdefault("motivo_negacao", None)
        if isinstance(params.get("sintomas_json"), list):
            params["sintomas_json"] = json.dumps(params["sintomas_json"])

        if self._dialect == "sqlite":
            # SQLite não suporta RETURNING: usa INSERT padrão + lastrowid
            sql_template = read_sql_file(_get_sql_path("inserir_pedido.sql"))
            # Remove a cláusula RETURNING do SQL para SQLite
            sql_clean = sql_template.split("RETURNING")[0].rstrip().rstrip(";")
            query_str = create_query(sql_clean, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            new_id = result.lastrowid
        else:
            sql_template = read_sql_file(_get_sql_path("inserir_pedido.sql"))
            query_str = create_query(sql_template, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            row = result.mappings().first()
            if row:
                row_dict = dict(row)
                if row_dict.get("paciente_prep"):
                    try:
                        row_dict["paciente_prep"] = decrypt_data(row_dict["paciente_prep"])
                    except Exception:
                        pass
                if row_dict.get("paciente_contato"):
                    try:
                        row_dict["paciente_contato"] = decrypt_data(row_dict["paciente_contato"])
                    except Exception:
                        pass
                if isinstance(row_dict.get("sintomas_json"), str):
                    try:
                        row_dict["sintomas_json"] = json.loads(row_dict["sintomas_json"])
                    except Exception:
                        pass
                return row_dict
            return {}


        # Para SQLite: busca o registro recém-inserido via SELECT
        select_sql = text(
            "SELECT id, paciente_prep, paciente_contato, medico_solicitante_crm, especialidade_id, "
            "sintomas_json, gravidade, status, marcado_por, data_consulta, motivo_negacao, criado_em, atualizado_em "
            "FROM interconsulta_pedidos WHERE id = :row_id"
        )
        sel_result = await self.session.execute(select_sql, {"row_id": new_id})
        row = sel_result.mappings().first()
        row_dict = dict(row) if row else {}
        if row_dict.get("paciente_prep"):
            try:
                row_dict["paciente_prep"] = decrypt_data(row_dict["paciente_prep"])
            except Exception:
                pass
        if row_dict.get("paciente_contato"):
            try:
                row_dict["paciente_contato"] = decrypt_data(row_dict["paciente_contato"])
            except Exception:
                pass
        if isinstance(row_dict.get("sintomas_json"), str):
            try:
                row_dict["sintomas_json"] = json.loads(row_dict["sintomas_json"])
            except Exception:
                pass
        return row_dict


    async def listar_pedidos_ativos(self, especialidade_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retorna todos os pedidos sem Soft Delete aplicado, ordenados por gravidade.
        Opcionalmente filtrado por especialidade_id.
        """
        sql_template = read_sql_file(_get_sql_path("listar_pedidos.sql"))
        result = await self.session.execute(text(sql_template))
        rows = result.mappings().all()

        pedidos = []
        for r in rows:
            p_dict = dict(r)
            if especialidade_id is not None and p_dict.get("especialidade_id") != especialidade_id:
                continue
            if p_dict.get("paciente_prep"):
                try:
                    p_dict["paciente_prep"] = decrypt_data(p_dict["paciente_prep"])
                except Exception:
                    pass
            if p_dict.get("paciente_contato"):
                try:
                    p_dict["paciente_contato"] = decrypt_data(p_dict["paciente_contato"])
                except Exception:
                    pass
            if isinstance(p_dict.get("sintomas_json"), str):
                try:
                    p_dict["sintomas_json"] = json.loads(p_dict["sintomas_json"])
                except Exception:
                    pass
            pedidos.append(p_dict)
        return pedidos


    async def inativar_pedido(self, pedido_id: int) -> bool:
        """
        Aplica Soft Delete no pedido especificado (LGPD: nunca deletar fisicamente).
        Retorna True se o pedido foi encontrado e atualizado.
        """
        if self._dialect == "sqlite":
            # SQLite não suporta RETURNING: usa UPDATE + rowcount
            update_sql = text(
                "UPDATE interconsulta_pedidos "
                "SET deleted_at = CURRENT_TIMESTAMP, atualizado_em = CURRENT_TIMESTAMP "
                "WHERE id = :id AND deleted_at IS NULL"
            )
            result = await self.session.execute(update_sql, {"id": pedido_id})
            await self.session.commit()
            return result.rowcount > 0
        else:
            sql_template = read_sql_file(_get_sql_path("soft_delete_pedido.sql"))
            query_str = create_query(sql_template, {"id": pedido_id})
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            row = result.mappings().first()
            return row is not None

    async def atualizar_status_pedido(self, pedido_id: int, novo_status: str, marcado_por: str = None, data_consulta: Any = None) -> bool:
        """
        Atualiza o status do pedido de interconsulta.
        Retorna True se o pedido foi atualizado com sucesso.
        """
        params = {"id": pedido_id, "status": novo_status, "marcado_por": marcado_por, "data_consulta": data_consulta}
        if self._dialect == "sqlite":
            update_sql = text(
                "UPDATE interconsulta_pedidos "
                "SET status = :status, marcado_por = :marcado_por, data_consulta = :data_consulta, atualizado_em = CURRENT_TIMESTAMP "
                "WHERE id = :id AND deleted_at IS NULL"
            )
            result = await self.session.execute(update_sql, params)
            await self.session.commit()
            return result.rowcount > 0
        else:
            sql_template = read_sql_file(_get_sql_path("atualizar_status_pedido.sql"))
            query_str = create_query(sql_template, params)
            result = await self.session.execute(text(query_str))
            await self.session.commit()
            row = result.mappings().first()
            return row is not None

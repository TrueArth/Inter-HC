import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from ..interfaces.interconsulta_provider_interface import InterconsultaProviderInterface
from src.helpers.crypto_helper import encrypt_data, decrypt_data
from cryptography.fernet import InvalidToken


class InterconsultaMockProvider(InterconsultaProviderInterface):
    """
    Mock data provider for Interconsulta.
    
    Persists data in a local JSON file ('data/interconsultas.json') to simulate a database.
    Applies AES encryption on 'paciente_prep' before saving and decrypts it on retrieval,
    matching the security behavior of the Postgres provider.
    """

    def __init__(self, file_path: str = "data/interconsultas.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensures the directory and mock JSON file exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _load_data(self) -> List[Dict[str, Any]]:
        """Loads data from the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]):
        """Saves data to the JSON file."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _parse_datetime(self, val: Any) -> Any:
        """Helper to parse ISO datetime strings into datetime objects."""
        if isinstance(val, str):
            try:
                # Handle Z offset standard in JavaScript/ISO strings
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except ValueError:
                pass
        return val

    def _decrypt_prep(self, encrypted_prep: str) -> str:
        """Safely decrypts patient PREP, falling back to original if decryption fails."""
        try:
            return decrypt_data(encrypted_prep)
        except (InvalidToken, Exception):
            # Graceful fallback: return as-is (useful if stored as plain text or key changed)
            return encrypted_prep

    async def inserir_pedido(self, pedido_data: dict) -> dict:
        """
        Inserts a new interconsultation request.
        
        Encrypts CNS before saving. Returns the decrypted representation for immediately usage.
        """
        data = self._load_data()
        
        # Calculate next ID
        next_id = max([item.get("id", 0) for item in data]) + 1 if data else 1
        
        now_str = datetime.now(timezone.utc).isoformat()
        
        prep_original = pedido_data.get("paciente_prep", "")
        prep_encrypted = encrypt_data(prep_original)
        
        contato_original = pedido_data.get("paciente_contato")
        contato_encrypted = encrypt_data(contato_original) if contato_original else None
        
        # Sintomas can be list or string
        sintomas = pedido_data.get("sintomas_json", [])
        if isinstance(sintomas, str):
            try:
                sintomas = json.loads(sintomas)
            except Exception:
                pass

        new_record = {
            "id": next_id,
            "paciente_prep": prep_encrypted,
            "paciente_contato": contato_encrypted,
            "medico_solicitante_crm": pedido_data.get("medico_solicitante_crm", ""),
            "especialidade_id": int(pedido_data.get("especialidade_id", 0)),
            "sintomas_json": sintomas,
            "gravidade": pedido_data.get("gravidade", "VERDE"),
            "status": pedido_data.get("status", "PENDENTE"),
            "marcado_por": pedido_data.get("marcado_por"),
            "data_consulta": None,
            "motivo_negacao": pedido_data.get("motivo_negacao"),
            "criado_em": now_str,
            "atualizado_em": now_str,
            "deleted_at": None
        }
        
        data.append(new_record)
        self._save_data(data)
        
        # Return record with parsed datetimes and decrypted CNS
        return {
            "id": new_record["id"],
            "paciente_prep": prep_original,
            "paciente_contato": contato_original,
            "medico_solicitante_crm": new_record["medico_solicitante_crm"],
            "especialidade_id": new_record["especialidade_id"],
            "sintomas_json": new_record["sintomas_json"],
            "gravidade": new_record["gravidade"],
            "status": new_record["status"],
            "marcado_por": new_record["marcado_por"],
            "data_consulta": None,
            "motivo_negacao": new_record["motivo_negacao"],
            "criado_em": self._parse_datetime(new_record["criado_em"]),
            "atualizado_em": self._parse_datetime(new_record["atualizado_em"])
        }

    async def listar_pedidos_ativos(self, especialidade_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lists all active requests (not soft-deleted), ordered by clinical gravity and creation date.
        Opcionalmente filtrado por especialidade_id.
        """
        data = self._load_data()
        
        active_records = []
        for r in data:
            if r.get("deleted_at") is not None:
                continue
                
            if especialidade_id is not None and int(r.get("especialidade_id", 0)) != especialidade_id:
                continue
                
            prep_decrypted = self._decrypt_prep(r.get("paciente_prep", ""))
            contato_encrypted = r.get("paciente_contato")
            contato_decrypted = self._decrypt_prep(contato_encrypted) if contato_encrypted else None
            
            active_records.append({
                "id": r["id"],
                "paciente_prep": prep_decrypted,
                "paciente_contato": contato_decrypted,
                "medico_solicitante_crm": r.get("medico_solicitante_crm", ""),
                "especialidade_id": int(r.get("especialidade_id", 0)),
                "sintomas_json": r.get("sintomas_json", []),
                "gravidade": r.get("gravidade", "VERDE"),
                "status": r.get("status", "PENDENTE"),
                "marcado_por": r.get("marcado_por"),
                "data_consulta": self._parse_datetime(r.get("data_consulta")),
                "motivo_negacao": r.get("motivo_negacao"),
                "criado_em": self._parse_datetime(r.get("criado_em")),
                "atualizado_em": self._parse_datetime(r.get("atualizado_em"))
            })
            
        # Sort clinical gravity: VERMELHO = 1, AMARELO = 2, VERDE = 3, others = 4
        def gravity_sort_key(item: Dict[str, Any]) -> int:
            g = item["gravidade"].upper()
            if g == "VERMELHO":
                return 1
            elif g == "AMARELO":
                return 2
            elif g == "VERDE":
                return 3
            else:
                return 4
                
        def creation_sort_key(item: Dict[str, Any]) -> datetime:
            c = item["criado_em"]
            if isinstance(c, datetime):
                return c
            return datetime.min
            
        # Sort by gravity primarily, then by creation date ascending
        active_records.sort(key=lambda x: (gravity_sort_key(x), creation_sort_key(x)))
        return active_records

    async def inativar_pedido(self, pedido_id: int) -> bool:
        """
        Performs a soft delete on the requested interconsultation.
        """
        data = self._load_data()
        found = False
        
        for r in data:
            if r["id"] == pedido_id and r.get("deleted_at") is None:
                r["deleted_at"] = datetime.now(timezone.utc).isoformat()
                r["atualizado_em"] = r["deleted_at"]
                found = True
                break
                
        if found:
            self._save_data(data)
            
        return found

    async def atualizar_status_pedido(self, pedido_id: int, novo_status: str, marcado_por: str = None, data_consulta: Any = None) -> bool:
        """
        Updates the status of the requested interconsultation.
        """
        data = self._load_data()
        found = False
        
        for r in data:
            if r["id"] == pedido_id and r.get("deleted_at") is None:
                r["status"] = novo_status
                r["marcado_por"] = marcado_por
                if data_consulta is not None:
                    if isinstance(data_consulta, datetime):
                        r["data_consulta"] = data_consulta.isoformat()
                    else:
                        r["data_consulta"] = str(data_consulta)
                r["atualizado_em"] = datetime.now(timezone.utc).isoformat()
                found = True
                break
                
        if found:
            self._save_data(data)
            
        return found

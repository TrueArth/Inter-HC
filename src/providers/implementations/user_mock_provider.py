import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from ..interfaces.user_provider_interface import UserProviderInterface

class UserMockProvider(UserProviderInterface):
    """
    Mock user provider that stores users in a local JSON file ('data/users.json').
    """

    def __init__(self, file_path: str = "data/users.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _load_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def inserir_usuario(self, user_data: dict) -> dict:
        data = self._load_data()
        next_id = max([item.get("id", 0) for item in data]) + 1 if data else 1
        now_str = datetime.now(timezone.utc).isoformat()

        new_record = {
            "id": next_id,
            "username": user_data.get("username"),
            "hashed_password": user_data.get("hashed_password"),
            "display_name": user_data.get("display_name"),
            "role": user_data.get("role"),
            "email": user_data.get("email"),
            "created_at": now_str,
            "updated_at": now_str,
            "deleted_at": None
        }
        data.append(new_record)
        self._save_data(data)
        
        # return user representation (omit hashed_password)
        res = dict(new_record)
        res.pop("hashed_password", None)
        return res

    async def listar_usuarios(self) -> List[Dict[str, Any]]:
        data = self._load_data()
        res = []
        for u in data:
            if u.get("deleted_at") is None:
                res_u = dict(u)
                res_u.pop("hashed_password", None)
                res.append(res_u)
        return res

    async def atualizar_usuario(self, user_id: int, user_data: dict) -> dict:
        data = self._load_data()
        now_str = datetime.now(timezone.utc).isoformat()
        
        for u in data:
            if u["id"] == user_id and u.get("deleted_at") is None:
                u["display_name"] = user_data.get("display_name", u["display_name"])
                u["role"] = user_data.get("role", u["role"])
                u["email"] = user_data.get("email", u["email"])
                u["updated_at"] = now_str
                self._save_data(data)
                res = dict(u)
                res.pop("hashed_password", None)
                return res
        return {}

    async def inativar_usuario(self, user_id: int) -> bool:
        data = self._load_data()
        now_str = datetime.now(timezone.utc).isoformat()
        for u in data:
            if u["id"] == user_id and u.get("deleted_at") is None:
                u["deleted_at"] = now_str
                u["updated_at"] = now_str
                self._save_data(data)
                return True
        return False

    async def buscar_usuario_por_username(self, username: str) -> Optional[dict]:
        data = self._load_data()
        for u in data:
            if u["username"] == username and u.get("deleted_at") is None:
                return dict(u)
        return None

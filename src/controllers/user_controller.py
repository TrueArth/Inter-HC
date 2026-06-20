from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from src.providers.interfaces.user_provider_interface import UserProviderInterface
from src.helpers.crypto_helper import hash_password

class UserController:
    """
    Controlador de negócios para a entidade Usuário.
    """

    @staticmethod
    async def criar_usuario(user_data: dict, provider: UserProviderInterface) -> dict:
        """
        Garante a unicidade do username, gera hash da senha e insere o usuário.
        """
        username = user_data.get("username", "").strip().lower()
        if not username:
            raise HTTPException(status_code=400, detail="Username é obrigatório")

        # Verifica se já existe
        existing = await provider.buscar_usuario_por_username(username)
        if existing:
            raise HTTPException(status_code=400, detail=f"O usuário '{username}' já está cadastrado.")

        # Prepara dados
        senha_plana = user_data.get("password")
        if not senha_plana:
            raise HTTPException(status_code=400, detail="Senha é obrigatória")

        user_data["username"] = username
        user_data["hashed_password"] = hash_password(senha_plana)
        
        # Remove a senha plana
        user_data_copy = dict(user_data)
        user_data_copy.pop("password", None)

        try:
            return await provider.inserir_usuario(user_data_copy)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar usuário: {str(e)}")

    @staticmethod
    async def listar_usuarios(provider: UserProviderInterface) -> List[Dict[str, Any]]:
        """
        Retorna a lista de usuários ativos.
        """
        try:
            return await provider.listar_usuarios()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")

    @staticmethod
    async def atualizar_usuario(user_id: int, user_data: dict, provider: UserProviderInterface) -> dict:
        """
        Atualiza dados do usuário.
        """
        try:
            updated = await provider.atualizar_usuario(user_id, user_data)
            if not updated:
                raise HTTPException(status_code=404, detail="Usuário não encontrado ou inativo.")
            return updated
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

    @staticmethod
    async def cancelar_usuario(user_id: int, provider: UserProviderInterface) -> dict:
        """
        Aplica o Soft Delete no usuário.
        """
        sucesso = await provider.inativar_usuario(user_id)
        if not sucesso:
            raise HTTPException(status_code=404, detail="Usuário não encontrado ou já cancelado.")
        return {"message": "Usuário desativado com sucesso."}

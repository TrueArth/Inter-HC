from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class UserProviderInterface(ABC):
    
    @abstractmethod
    async def inserir_usuario(self, user_data: dict) -> dict:
        """
        Insere um novo usuário.
        Retorna o dicionário representando o usuário criado.
        """
        pass
        
    @abstractmethod
    async def listar_usuarios(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de usuários ativos.
        """
        pass
        
    @abstractmethod
    async def atualizar_usuario(self, user_id: int, user_data: dict) -> dict:
        """
        Atualiza os dados de um usuário ativo.
        Retorna o dicionário representando o usuário atualizado.
        """
        pass
        
    @abstractmethod
    async def inativar_usuario(self, user_id: int) -> bool:
        """
        Aplica Soft Delete no usuário especificado.
        Retorna True em caso de sucesso.
        """
        pass

    @abstractmethod
    async def buscar_usuario_por_username(self, username: str) -> Optional[dict]:
        """
        Busca um usuário ativo por seu username.
        Retorna o dicionário do usuário ou None se não encontrado.
        """
        pass

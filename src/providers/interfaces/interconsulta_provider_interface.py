from abc import ABC, abstractmethod
from typing import List, Dict, Any

class InterconsultaProviderInterface(ABC):
    
    @abstractmethod
    async def inserir_pedido(self, pedido_data: dict) -> dict:
        """
        Insere um novo pedido de interconsulta no banco de dados.
        Retorna o dicionário representando o pedido recém-criado.
        """
        pass
        
    @abstractmethod
    async def listar_pedidos_ativos(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os pedidos que não sofreram Soft Delete,
        ordenados por gravidade.
        """
        pass
        
    @abstractmethod
    async def inativar_pedido(self, pedido_id: int) -> bool:
        """
        Aplica o Soft Delete no pedido especificado.
        Retorna True em caso de sucesso.
        """
        pass

    @abstractmethod
    async def atualizar_status_pedido(self, pedido_id: int, novo_status: str, marcado_por: str = None) -> bool:
        """
        Atualiza o status de um pedido de interconsulta.
        Retorna True em caso de sucesso.
        """
        pass

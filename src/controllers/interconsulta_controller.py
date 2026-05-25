from fastapi import HTTPException, BackgroundTasks
from typing import List, Dict, Any
from cryptography.fernet import InvalidToken

from src.providers.interfaces.interconsulta_provider_interface import InterconsultaProviderInterface
from src.services.risk_engine_service import RiskEngineService
from src.helpers.messaging_helper import MessageBroker
from src.workers.central_marcacao_worker import enviar_para_central_aghu

def _format_error(exc: Exception) -> str:
    """Mensagem legível para HTTP detail (ex.: InvalidToken tem str vazio)."""
    if isinstance(exc, InvalidToken):
        return (
            "Não foi possível descriptografar o CNS. "
            "A AES_SECRET_KEY do .env mudou desde que os pedidos foram gravados. "
            "Apague os registros antigos em interconsulta_pedidos ou restaure a chave anterior."
        )
    return str(exc) or f"{type(exc).__name__}"


class InterconsultaController:
    """
    Controlador responsável por orquestrar a criação de interconsultas.
    Aplica o motor de regras, delega a persistência e enfileira no Message Broker.
    """
    
    @staticmethod
    async def solicitar_interconsulta(
        payload: dict, 
        provider: InterconsultaProviderInterface,
        background_tasks: BackgroundTasks
    ) -> dict:
        """
        Recebe o payload da API, processa e persiste a interconsulta.
        """
        sintomas = payload.get("sintomas_json", [])
        
        # 1. Processamento pelo Motor de Regras
        gravidade = RiskEngineService.calcular_gravidade(sintomas)
        payload["gravidade"] = gravidade
        payload["status"] = "ENFILEIRADO"
        
        # 2. Persistência de Dados via Provider (Criptografia e Soft Delete aplicados no provider)
        try:
            pedido_criado = await provider.inserir_pedido(payload)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar o pedido: {_format_error(e)}")
            
        # 3. Publicação no Message Broker (Assíncrono)
        MessageBroker.dispatch(background_tasks, enviar_para_central_aghu, pedido_criado)
        
        return pedido_criado

    @staticmethod
    async def listar_pedidos(provider: InterconsultaProviderInterface) -> List[Dict[str, Any]]:
        """
        Retorna as interconsultas ativas.
        """
        try:
            return await provider.listar_pedidos_ativos()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar pedidos: {_format_error(e)}")
            
    @staticmethod
    async def cancelar_pedido(pedido_id: int, provider: InterconsultaProviderInterface) -> dict:
        """
        Aplica o Soft Delete no pedido.
        """
        sucesso = await provider.inativar_pedido(pedido_id)
        if not sucesso:
            raise HTTPException(status_code=404, detail="Pedido não encontrado ou já cancelado.")
        return {"message": "Pedido cancelado com sucesso."}

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
    async def listar_pedidos(provider: InterconsultaProviderInterface, current_user: dict) -> List[Dict[str, Any]]:
        """
        Retorna as interconsultas ativas.
        """
        try:
            pedidos = await provider.listar_pedidos_ativos()
            # Trilha de Auditoria (LGPD)
            username = current_user.get("username") or current_user.get("name") or "Desconhecido"
            import logging
            logger = logging.getLogger("audit")
            logger.warning(
                f"AUDITORIA: Usuario '{username}' visualizou os dados sensiveis (CNS) de {len(pedidos)} pedido(s) de interconsulta."
            )
            return pedidos
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

    @staticmethod
    async def atualizar_status(pedido_id: int, status: str, provider: InterconsultaProviderInterface) -> dict:
        """
        Atualiza o status de um pedido de interconsulta.
        """
        try:
            sucesso = await provider.atualizar_status_pedido(pedido_id, status)
            if not sucesso:
                raise HTTPException(status_code=404, detail="Pedido não encontrado ou inativo.")
            return {"message": "Status atualizado com sucesso.", "pedido_id": pedido_id, "novo_status": status}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {_format_error(e)}")

    @staticmethod
    async def reprocessar_envio(
        pedido_id: int, 
        provider: InterconsultaProviderInterface, 
        background_tasks: BackgroundTasks
    ) -> dict:
        """
        Força o re-enfileiramento de um pedido com status de ERRO.
        """
        try:
            # 1. Busca os pedidos ativos para encontrar o correspondente
            pedidos = await provider.listar_pedidos_ativos()
            pedido = next((p for p in pedidos if p["id"] == pedido_id), None)
            
            if not pedido:
                raise HTTPException(status_code=404, detail="Pedido não encontrado ou inativo.")
                
            if pedido.get("status") not in ["ERRO", "PENDENTE", "ENFILEIRADO"]:
                raise HTTPException(status_code=400, detail=f"Apenas pedidos com falha ou pendentes podem ser re-enviados. Status atual: {pedido.get('status')}")
                
            # 2. Atualiza o status para ENFILEIRADO
            await provider.atualizar_status_pedido(pedido_id, "ENFILEIRADO")
            pedido["status"] = "ENFILEIRADO"
            
            # 3. Dispara o worker assíncrono
            MessageBroker.dispatch(background_tasks, enviar_para_central_aghu, pedido)
            
            return {"message": "Re-envio disparado com sucesso.", "pedido_id": pedido_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao reprocessar envio: {_format_error(e)}")

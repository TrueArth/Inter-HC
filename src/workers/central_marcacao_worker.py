import asyncio
import logging
import os

logger = logging.getLogger(__name__)

async def update_status_in_worker(pedido_id: int, status: str):
    """
    Atualiza o status do pedido no banco de dados local a partir do worker em background,
    decidindo entre o provedor Mock ou Postgres com base nas variáveis de ambiente.
    """
    strategy = os.getenv("INTERCONSULTA_PROVIDER_TYPE", "POSTGRES")
    if strategy.upper() == "MOCK":
        from src.providers.implementations.interconsulta_mock_provider import InterconsultaMockProvider
        provider = InterconsultaMockProvider()
        await provider.atualizar_status_pedido(pedido_id, status)
    else:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from src.providers.implementations.interconsulta_postgres_provider import InterconsultaPostgresProvider
        
        dsn = os.getenv("SQLITE_DSN") or os.getenv("POSTGRES_DSN")
        if not dsn:
            logger.error("DSN nao configurado no ambiente para atualizacao no worker.")
            return
            
        engine = create_async_engine(dsn, echo=False)
        async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        dialect = engine.bind.dialect.name if engine.bind else "postgresql"
        
        try:
            async with async_session_maker() as session:
                provider = InterconsultaPostgresProvider(session=session, dialect=dialect)
                await provider.atualizar_status_pedido(pedido_id, status)
        except Exception as e:
            logger.error(f"Erro ao salvar status {status} para o pedido {pedido_id} no worker: {e}")
        finally:
            await engine.dispose()

async def enviar_para_central_aghu(pedido_dict: dict, retry_count: int = 0):
    """
    Worker assíncrono que simula o envio do pedido de interconsulta para a Central de Marcação do AGHU.
    Implementa um backoff exponencial simples para simular resiliência a falhas (HTTP 503/500).
    """
    MAX_RETRIES = 3
    try:
        logger.info(f"Iniciando envio do pedido {pedido_dict.get('id')} para o AGHU. Tentativa {retry_count + 1}")
        
        # Simulação de latência de rede
        await asyncio.sleep(2)
        
        # AQUI entraria a chamada HTTP real (ex: httpx.post)
        # Vamos simular um sucesso garantido neste boilerplate
        sucesso_api = True 
        
        if sucesso_api:
            logger.info(f"Sucesso: Pedido {pedido_dict.get('id')} processado pela Central de Marcação.")
            await update_status_in_worker(pedido_dict.get('id'), 'PENDENTE')
        else:
            raise Exception("HTTP 503 Service Unavailable")
            
    except Exception as e:
        logger.error(f"Erro ao enviar pedido {pedido_dict.get('id')}: {str(e)}")
        if retry_count < MAX_RETRIES:
            wait_time = 2 ** retry_count  # Exponencial: 1s, 2s, 4s...
            logger.warning(f"Re-enfileirando pedido {pedido_dict.get('id')} em {wait_time} segundos...")
            await asyncio.sleep(wait_time)
            await enviar_para_central_aghu(pedido_dict, retry_count + 1)
        else:
            logger.critical(f"Falha definitiva ao enviar o pedido {pedido_dict.get('id')} após {MAX_RETRIES} tentativas.")
            await update_status_in_worker(pedido_dict.get('id'), 'ERRO')

from fastapi import BackgroundTasks
import asyncio
import logging

logger = logging.getLogger(__name__)

class MessageBroker:
    """
    Simula um Message Broker (como Celery/Redis) usando BackgroundTasks do FastAPI.
    Útil para o ambiente de desenvolvimento local conforme definido na arquitetura.
    """
    @staticmethod
    def dispatch(background_tasks: BackgroundTasks, worker_func, *args, **kwargs):
        """
        Enfileira uma função para ser executada em background.
        """
        logger.info(f"Enfileirando tarefa assíncrona: {worker_func.__name__}")
        background_tasks.add_task(worker_func, *args, **kwargs)

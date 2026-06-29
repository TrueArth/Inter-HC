import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import BackgroundTasks

from src.controllers.interconsulta_controller import InterconsultaController
from src.providers.interfaces.interconsulta_provider_interface import InterconsultaProviderInterface

@pytest.mark.asyncio
async def test_solicitar_interconsulta_com_sintoma_critico():
    # Arrange
    mock_provider = AsyncMock(spec=InterconsultaProviderInterface)
    mock_provider.inserir_pedido.return_value = {"id": 1, "gravidade": "VERMELHO"}
    mock_bg_tasks = MagicMock(spec=BackgroundTasks)
    
    payload = {
        "paciente_cns": "123",
        "medico_solicitante_crm": "PE-123",
        "especialidade_id": 1,
        # O ID 1 é crítico conforme RiskEngineService
        "sintomas_json": [{"id": 1, "nome": "Cegueira"}]
    }

    # Act
    resultado = await InterconsultaController.solicitar_interconsulta(payload, mock_provider, mock_bg_tasks)

    # Assert
    assert resultado["gravidade"] == "VERMELHO"
    mock_provider.inserir_pedido.assert_called_once()
    # Verifica se a gravidade VERMELHO foi injetada no payload antes de salvar
    args, _ = mock_provider.inserir_pedido.call_args
    assert args[0]["gravidade"] == "VERMELHO"
    assert args[0]["status"] == "PENDENTE"
    # Verifica se o worker assíncrono NÃO foi disparado na BackgroundTask
    mock_bg_tasks.add_task.assert_not_called()

@pytest.mark.asyncio
async def test_solicitar_interconsulta_sem_sintomas_criticos():
    # Arrange
    mock_provider = AsyncMock(spec=InterconsultaProviderInterface)
    mock_provider.inserir_pedido.return_value = {"id": 2, "gravidade": "VERDE"}
    mock_bg_tasks = MagicMock(spec=BackgroundTasks)
    
    payload = {
        "paciente_cns": "123",
        "sintomas_json": [{"id": 99, "nome": "Leve desconforto"}]
    }

    # Act
    resultado = await InterconsultaController.solicitar_interconsulta(payload, mock_provider, mock_bg_tasks)

    # Assert
    # Sem ID crítico ou moderado (IDs 1 a 6 mapeados no engine), o retorno padrão é VERDE
    args, _ = mock_provider.inserir_pedido.call_args
    assert args[0]["gravidade"] == "VERDE"
    assert args[0]["status"] == "ERRO"
    assert args[0]["motivo_negacao"] == "Não é papel do HC"
    mock_bg_tasks.add_task.assert_not_called()

@pytest.mark.asyncio
async def test_solicitar_interconsulta_com_override_especialidade_cardiologia():
    # Arrange
    mock_provider = AsyncMock(spec=InterconsultaProviderInterface)
    mock_provider.inserir_pedido.side_effect = lambda x: x
    mock_bg_tasks = MagicMock(spec=BackgroundTasks)
    
    payload = {
        "paciente_cns": "123",
        "especialidade_id": 1, # Cardiologia
        "sintomas_json": [{"id": 4, "nome": "Dor torácica intensa"}] # ID 4 -> override p/ VERMELHO em Cardiologia
    }

    # Act
    resultado = await InterconsultaController.solicitar_interconsulta(payload, mock_provider, mock_bg_tasks)

    # Assert
    assert resultado["gravidade"] == "VERMELHO"

@pytest.mark.asyncio
async def test_solicitar_interconsulta_sem_override_especialidade():
    # Arrange
    mock_provider = AsyncMock(spec=InterconsultaProviderInterface)
    mock_provider.inserir_pedido.side_effect = lambda x: x
    mock_bg_tasks = MagicMock(spec=BackgroundTasks)
    
    payload = {
        "paciente_cns": "123",
        "especialidade_id": 2, # Clínica Médica
        "sintomas_json": [{"id": 4, "nome": "Dor torácica intensa"}] # ID 4 -> Padrão AMARELO
    }

    # Act
    resultado = await InterconsultaController.solicitar_interconsulta(payload, mock_provider, mock_bg_tasks)

    # Assert
    assert resultado["gravidade"] == "AMARELO"

@pytest.mark.asyncio
async def test_solicitar_interconsulta_com_override_dermatologia():
    # Arrange
    mock_provider = AsyncMock(spec=InterconsultaProviderInterface)
    mock_provider.inserir_pedido.side_effect = lambda x: x
    mock_bg_tasks = MagicMock(spec=BackgroundTasks)
    
    payload = {
        "paciente_cns": "123",
        "especialidade_id": 3, # Dermatologia
        "sintomas_json": [{"id": 13, "nome": "Erupção cutânea com febre"}] # ID 13 -> override p/ AMARELO em Dermatologia
    }

    # Act
    resultado = await InterconsultaController.solicitar_interconsulta(payload, mock_provider, mock_bg_tasks)

    # Assert
    assert resultado["gravidade"] == "AMARELO"

@pytest.mark.asyncio
async def test_solicitar_interconsulta_sem_override_dermatologia():
    # Arrange
    mock_provider = AsyncMock(spec=InterconsultaProviderInterface)
    mock_provider.inserir_pedido.side_effect = lambda x: x
    mock_bg_tasks = MagicMock(spec=BackgroundTasks)
    
    payload = {
        "paciente_cns": "123",
        "especialidade_id": 2, # Clínica Médica
        "sintomas_json": [{"id": 13, "nome": "Erupção cutânea com febre"}] # ID 13 -> Padrão VERDE
    }

    # Act
    resultado = await InterconsultaController.solicitar_interconsulta(payload, mock_provider, mock_bg_tasks)

    # Assert
    assert resultado["gravidade"] == "VERDE"


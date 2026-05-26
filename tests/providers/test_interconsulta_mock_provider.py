import pytest
import os
import json
from datetime import datetime
from src.providers.implementations.interconsulta_mock_provider import InterconsultaMockProvider

@pytest.fixture
def mock_db_file(tmp_path):
    """Provides a path to a temporary JSON file to avoid writing to development data."""
    file_path = tmp_path / "interconsultas_test.json"
    return str(file_path)

@pytest.mark.asyncio
async def test_mock_provider_workflow(mock_db_file):
    provider = InterconsultaMockProvider(file_path=mock_db_file)
    
    # Initially the database file is an empty list
    assert provider._load_data() == []
    
    # 1. Insert a new interconsultation request
    novo_pedido = {
        "paciente_cns": "987654321012345",
        "medico_solicitante_crm": "54321-PE",
        "especialidade_id": 2,
        "sintomas_json": [{"id": 5, "nome": "Febre"}],
        "gravidade": "AMARELO",
        "status": "PENDENTE"
    }
    
    criado = await provider.inserir_pedido(novo_pedido)
    assert criado["id"] == 1
    assert criado["paciente_cns"] == "987654321012345"
    assert criado["medico_solicitante_crm"] == "54321-PE"
    assert criado["gravidade"] == "AMARELO"
    assert isinstance(criado["criado_em"], datetime)
    
    # Ensure that on-disk representation is securely encrypted
    raw_records = provider._load_data()
    assert len(raw_records) == 1
    assert raw_records[0]["paciente_cns"] != "987654321012345"
    
    # 2. List requests (must automatically decrypt)
    pedidos = await provider.listar_pedidos_ativos()
    assert len(pedidos) == 1
    assert pedidos[0]["id"] == 1
    assert pedidos[0]["paciente_cns"] == "987654321012345"
    
    # 3. Soft Delete the request
    sucesso = await provider.inativar_pedido(1)
    assert sucesso is True
    
    # 4. Active list should be empty now
    pedidos_ativos = await provider.listar_pedidos_ativos()
    assert len(pedidos_ativos) == 0
    
    # Verify that the record is soft-deleted on disk (contains a deleted_at timestamp)
    raw_records = provider._load_data()
    assert len(raw_records) == 1
    assert raw_records[0]["deleted_at"] is not None

@pytest.mark.asyncio
async def test_mock_provider_sorting(mock_db_file):
    provider = InterconsultaMockProvider(file_path=mock_db_file)
    
    # Insert multiple records with different severities
    # 1. AMARELO first
    await provider.inserir_pedido({
        "paciente_cns": "111",
        "gravidade": "AMARELO",
        "especialidade_id": 1,
        "status": "PENDENTE"
    })
    
    # 2. VERMELHO second
    await provider.inserir_pedido({
        "paciente_cns": "222",
        "gravidade": "VERMELHO",
        "especialidade_id": 1,
        "status": "PENDENTE"
    })
    
    # 3. VERDE third
    await provider.inserir_pedido({
        "paciente_cns": "333",
        "gravidade": "VERDE",
        "especialidade_id": 1,
        "status": "PENDENTE"
    })
    
    # List active requests - must be sorted by priority: VERMELHO -> AMARELO -> VERDE
    pedidos = await provider.listar_pedidos_ativos()
    assert len(pedidos) == 3
    assert pedidos[0]["gravidade"] == "VERMELHO"
    assert pedidos[0]["paciente_cns"] == "222"
    assert pedidos[1]["gravidade"] == "AMARELO"
    assert pedidos[1]["paciente_cns"] == "111"
    assert pedidos[2]["gravidade"] == "VERDE"
    assert pedidos[2]["paciente_cns"] == "333"

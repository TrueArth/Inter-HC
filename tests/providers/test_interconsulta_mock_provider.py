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
        "paciente_prep": "7700201",
        "medico_solicitante_crm": "54321-PE",
        "especialidade_id": 2,
        "sintomas_json": [{"id": 5, "nome": "Febre"}],
        "gravidade": "AMARELO",
        "status": "PENDENTE"
    }
    
    criado = await provider.inserir_pedido(novo_pedido)
    assert criado["id"] == 1
    assert criado["paciente_prep"] == "7700201"
    assert criado["medico_solicitante_crm"] == "54321-PE"
    assert criado["gravidade"] == "AMARELO"
    assert isinstance(criado["criado_em"], datetime)
    
    # Ensure that on-disk representation is securely encrypted
    raw_records = provider._load_data()
    assert len(raw_records) == 1
    assert raw_records[0]["paciente_prep"] != "7700201"
    
    # 2. List requests (must automatically decrypt)
    pedidos = await provider.listar_pedidos_ativos()
    assert len(pedidos) == 1
    assert pedidos[0]["id"] == 1
    assert pedidos[0]["paciente_prep"] == "7700201"
    
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
        "paciente_prep": "7700201",
        "gravidade": "AMARELO",
        "especialidade_id": 1,
        "status": "PENDENTE"
    })
    
    # 2. VERMELHO second
    await provider.inserir_pedido({
        "paciente_prep": "7700301",
        "gravidade": "VERMELHO",
        "especialidade_id": 1,
        "status": "PENDENTE"
    })
    
    # 3. VERDE third
    await provider.inserir_pedido({
        "paciente_prep": "7700401",
        "gravidade": "VERDE",
        "especialidade_id": 1,
        "status": "PENDENTE"
    })
    
    # List active requests - must be sorted by priority: VERMELHO -> AMARELO -> VERDE
    pedidos = await provider.listar_pedidos_ativos()
    assert len(pedidos) == 3
    assert pedidos[0]["gravidade"] == "VERMELHO"
    assert pedidos[0]["paciente_prep"] == "7700301"
    assert pedidos[1]["gravidade"] == "AMARELO"
    assert pedidos[1]["paciente_prep"] == "7700201"
    assert pedidos[2]["gravidade"] == "VERDE"
    assert pedidos[2]["paciente_prep"] == "7700401"

@pytest.mark.asyncio
async def test_atualizar_status_pedido_success(mock_db_file):
    """Atualizar o status de um pedido existente deve retornar True e persistir no disco."""
    provider = InterconsultaMockProvider(file_path=mock_db_file)
    await provider.inserir_pedido({
        "paciente_prep": "10000016",
        "medico_solicitante_crm": "12345-PE",
        "especialidade_id": 1,
        "sintomas_json": [{"id": 1, "nome": "Cegueira"}],
        "gravidade": "VERMELHO",
        "status": "PENDENTE"
    })

    sucesso = await provider.atualizar_status_pedido(1, "AGENDADO")
    assert sucesso is True

    # Verifica no disco que o status foi persistido
    raw = provider._load_data()
    assert raw[0]["status"] == "AGENDADO"
    assert raw[0]["atualizado_em"] is not None

@pytest.mark.asyncio
async def test_atualizar_status_pedido_nao_encontrado(mock_db_file):
    """Tentar atualizar um ID inexistente deve retornar False."""
    provider = InterconsultaMockProvider(file_path=mock_db_file)

    sucesso = await provider.atualizar_status_pedido(999, "AGENDADO")
    assert sucesso is False

@pytest.mark.asyncio
async def test_atualizar_status_pedido_ignorado_apos_soft_delete(mock_db_file):
    """Um pedido com soft delete não deve ter seu status alterado."""
    provider = InterconsultaMockProvider(file_path=mock_db_file)
    await provider.inserir_pedido({
        "paciente_prep": "7700401",
        "medico_solicitante_crm": "99999-PE",
        "especialidade_id": 3,
        "sintomas_json": [],
        "gravidade": "VERDE",
        "status": "PENDENTE"
    })

    # Soft-delete o pedido
    await provider.inativar_pedido(1)

    # Tentativa de atualização deve retornar False (deleted_at não é None)
    sucesso = await provider.atualizar_status_pedido(1, "AGENDADO")
    assert sucesso is False

    # O status no disco deve permanecer inalterado
    raw = provider._load_data()
    assert raw[0]["status"] == "PENDENTE"

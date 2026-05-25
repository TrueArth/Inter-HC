#!/bin/bash

# Mata apenas os processos uvicorn vinculados a esta aplicação para liberar a porta 8000
pkill -f "uvicorn src.main:app" || true

echo "Iniciando a aplicação com uv run..."

# Executa o uvicorn via uv run para garantir o uso do ambiente correto
# O log é redirecionado para server.log e o processo roda em background usando nohup
nohup uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &

echo "Aplicação iniciada! Acompanhe os logs com: tail -f server.log"

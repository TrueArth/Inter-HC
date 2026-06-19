import os
import sys
import json
from datetime import datetime, timedelta, timezone

# Adiciona a raiz do projeto ao sys.path para conseguirmos importar o src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.helpers.crypto_helper import encrypt_data

# Configuração do caminho do "Banco de Dados" (Mock JSON)
FILE_PATH = "data/interconsultas.json"

def criar_data_passada(dias_atras: int) -> str:
    """Gera uma string ISO de uma data no passado."""
    data_passada = datetime.now(timezone.utc) - timedelta(days=dias_atras)
    return data_passada.isoformat()

def popular_banco():
    print("🌱 Iniciando o semeador de casos clínicos fictícios...")
    
    # Garante que a pasta data/ existe
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    
    # Os 3 Casos de Teste para a Apresentação
    casos = [
        {
            "id": 1,
            # Caso 1: O "Esquecido" (Inanição). Amarelo, esperando há 20 dias!
            "paciente_cns": encrypt_data("111111111111111"), 
            "medico_solicitante_crm": "12345-PE",
            "especialidade_id": 2, # Cardiologia, por exemplo
            "sintomas_json": [{"id": 4, "nome": "Dor torácica moderada"}],
            "gravidade": "AMARELO",
            "status": "PENDENTE",
            "criado_em": criar_data_passada(20), # 20 dias na fila
            "atualizado_em": criar_data_passada(20),
            "deleted_at": None
        },
        {
            "id": 2,
            # Caso Extra: Apenas um paciente de rotina antigo na fila
            "paciente_cns": encrypt_data("222222222222222"),
            "medico_solicitante_crm": "54321-PE",
            "especialidade_id": 2,
            "sintomas_json": [{"id": 1, "nome": "Checkup de rotina"}],
            "gravidade": "VERDE",
            "status": "PENDENTE",
            "criado_em": criar_data_passada(5), # 5 dias na fila
            "atualizado_em": criar_data_passada(5),
            "deleted_at": None
        },
        {
            "id": 3,
            # Caso do "Fura Fila Justo". Infartado, entrou HOJE.
            "paciente_cns": encrypt_data("333333333333333"),
            "medico_solicitante_crm": "99999-PE",
            "especialidade_id": 2,
            "sintomas_json": [{"id": 2, "nome": "Infarto"}],
            "gravidade": "VERMELHO",
            "status": "PENDENTE",
            "criado_em": criar_data_passada(0), # Entrou hoje
            "atualizado_em": criar_data_passada(0),
            "deleted_at": None
        }
    ]

    # Salva diretamente no arquivo JSON simulando o banco
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(casos, f, indent=2, ensure_ascii=False)

    print(f"✅ Banco de dados populado com sucesso em '{FILE_PATH}'!")
    print("🧑‍⚕️ Pacientes criados:")
    print("   1. Seu João (Amarelo) - Aguardando há 20 dias")
    print("   2. Dona Ana (Verde) - Aguardando há 5 dias")
    print("   3. Sr. Carlos (Vermelho) - Entrou hoje")

if __name__ == "__main__":
    popular_banco()
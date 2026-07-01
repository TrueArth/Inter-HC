import os
import sys
import json
import csv
from datetime import datetime, timedelta, timezone

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.helpers.crypto_helper import encrypt_data

PACIENTES_CSV = "data/pacientes.csv"
INTERCONSULTAS_JSON = "data/interconsultas.json"

def criar_data_passada(dias_atras: int) -> str:
    data_passada = datetime.now(timezone.utc) - timedelta(days=dias_atras)
    return data_passada.isoformat()

def main():
    print("Generating realistic mock patients...")
    os.makedirs("data", exist_ok=True)
    
    # 1. Patients Data
    pacientes = [
        {
            "codigo": "10000016",
            "nome": "Carla Maria Dias",
            "prep": "10000016",
            "dt_nascimento": "1985-03-10",
            "cpf": "482.918.230-10",
            "sexo": "F",
            "cor": "BRANCA",
            "nome_mae": "Sandra Regina Dias",
            "nome_pai": "Roberto Carlos Dias",
            "data_hora_inicio": "2026-06-25 09:00",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Clínica Médica",
            "procedimento": "(null)"
        },
        {
            "codigo": "7700201",
            "nome": "Bruno Ricardo Lima",
            "prep": "7700201",
            "dt_nascimento": "1991-07-22",
            "cpf": "928.374.019-45",
            "sexo": "M",
            "cor": "PARDA",
            "nome_mae": "Fatima Maria Lima",
            "nome_pai": "Jorge Luis Lima",
            "data_hora_inicio": "2026-06-25 10:30",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Ortopedia",
            "procedimento": "(null)"
        },
        {
            "codigo": "7700301",
            "nome": "Fernanda Souza Costa",
            "prep": "7700301",
            "dt_nascimento": "2001-11-01",
            "cpf": "103.829.475-80",
            "sexo": "F",
            "cor": "BRANCA",
            "nome_mae": "Vera Lúcia Costa",
            "nome_pai": "Marcos Antônio Costa",
            "data_hora_inicio": "2026-06-25 14:00",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Dermatologia",
            "procedimento": "Biópsia de pele"
        },
        {
            "codigo": "7700401",
            "nome": "Lucas Alberto Almeida",
            "prep": "7700401",
            "dt_nascimento": "1988-02-18",
            "cpf": "382.910.482-19",
            "sexo": "M",
            "cor": "PRETA",
            "nome_mae": "Regina Célia Almeida",
            "nome_pai": "Antonio Francisco Almeida",
            "data_hora_inicio": "2026-06-26 08:00",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Cardiologia",
            "procedimento": "Eletrocardiograma"
        },
        {
            "codigo": "55502931",
            "nome": "Maria José Silva",
            "prep": "55502931",
            "dt_nascimento": "1975-05-15",
            "cpf": "728.391.029-55",
            "sexo": "F",
            "cor": "PARDA",
            "nome_mae": "Alzira Maria Silva",
            "nome_pai": "Jose Valdevino Silva",
            "data_hora_inicio": "2026-06-26 09:30",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Clínica Médica",
            "procedimento": "(null)"
        },
        {
            "codigo": "66601928",
            "nome": "João Pedro Santos",
            "prep": "66601928",
            "dt_nascimento": "1968-09-20",
            "cpf": "294.857.301-82",
            "sexo": "M",
            "cor": "BRANCA",
            "nome_mae": "Lurdes Maria Santos",
            "nome_pai": "Manuel Antonio Santos",
            "data_hora_inicio": "2026-06-26 11:00",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Cardiologia",
            "procedimento": "(null)"
        },
        {
            "codigo": "77703847",
            "nome": "Ana Julia Oliveira",
            "prep": "77703847",
            "dt_nascimento": "1980-04-12",
            "cpf": "837.291.048-22",
            "sexo": "F",
            "cor": "PRETA",
            "nome_mae": "Carla Cristina Oliveira",
            "nome_pai": "Julio Cesar Oliveira",
            "data_hora_inicio": "2026-06-27 13:00",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Neurologia",
            "procedimento": "(null)"
        },
        {
            "codigo": "88804928",
            "nome": "Roberto Eduardo Souza",
            "prep": "88804928",
            "dt_nascimento": "1993-12-05",
            "cpf": "192.837.465-91",
            "sexo": "M",
            "cor": "PARDA",
            "nome_mae": "Regina Maria Souza",
            "nome_pai": "Afonso Celso Souza",
            "data_hora_inicio": "2026-06-27 15:30",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Ortopedia",
            "procedimento": "(null)"
        },
        {
            "codigo": "12345678",
            "nome": "Mariana Silva (Teste)",
            "prep": "12345678",
            "dt_nascimento": "1995-08-12",
            "cpf": "528.391.029-44",
            "sexo": "F",
            "cor": "BRANCA",
            "nome_mae": "Maria das Graças Silva",
            "nome_pai": "Pedro Silva",
            "data_hora_inicio": "2026-06-28 10:00",
            "status_consulta": "PACIENTE AGENDADO",
            "especialidade": "Pneumologia",
            "procedimento": "(null)"
        }
    ]

    
    # Save CSV
    headers = [
        "codigo", "nome", "prep", "dt_nascimento", "cpf", "sexo", "cor",
        "nome_mae", "nome_pai", "data_hora_inicio", "status_consulta",
        "especialidade", "procedimento"
    ]
    with open(PACIENTES_CSV, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(pacientes)
        
    print(f"Patient list saved in {PACIENTES_CSV}")
    
    # 2. Interconsultas Data
    interconsultas = [
        {
            "id": 1,
            "paciente_prep": encrypt_data("10000016"),
            "paciente_contato": encrypt_data("(81) 98888-7777"),
            "medico_solicitante_crm": "Dr. Carlos Silva",
            "especialidade_id": 1,
            "sintomas_json": [{"id": 4, "nome": "Dor torácica intensa"}],
            "gravidade": "VERMELHO",
            "status": "AGENDADO",
            "marcado_por": "admin",
            "data_consulta": criar_data_passada(-1),
            "motivo_negacao": None,
            "criado_em": criar_data_passada(5),
            "atualizado_em": criar_data_passada(1),
            "deleted_at": None
        },
        {
            "id": 2,
            "paciente_prep": encrypt_data("7700201"),
            "paciente_contato": encrypt_data("(81) 97777-6666"),
            "medico_solicitante_crm": "Dr. Carlos Silva",
            "especialidade_id": 1,
            "sintomas_json": [{"id": 2, "nome": "Infarto / Dor torácica súbita"}],
            "gravidade": "VERMELHO",
            "status": "PENDENTE",
            "marcado_por": None,
            "data_consulta": None,
            "motivo_negacao": None,
            "criado_em": criar_data_passada(3),
            "atualizado_em": criar_data_passada(3),
            "deleted_at": None
        },
        {
            "id": 3,
            "paciente_prep": encrypt_data("7700301"),
            "paciente_contato": None,
            "medico_solicitante_crm": "Dr. Roberto Souza",
            "especialidade_id": 2,
            "sintomas_json": [{"id": 14, "nome": "Confusão mental aguda"}],
            "gravidade": "AMARELO",
            "status": "PENDENTE",
            "marcado_por": None,
            "data_consulta": None,
            "motivo_negacao": None,
            "criado_em": criar_data_passada(4),
            "atualizado_em": criar_data_passada(4),
            "deleted_at": None
        },
        {
            "id": 4,
            "paciente_prep": encrypt_data("7700401"),
            "paciente_contato": encrypt_data("(81) 96666-5555"),
            "medico_solicitante_crm": "Dr. Roberto Souza",
            "especialidade_id": 3,
            "sintomas_json": [{"id": 6, "nome": "Fratura"}],
            "gravidade": "VERDE",
            "status": "PENDENTE",
            "marcado_por": None,
            "data_consulta": None,
            "motivo_negacao": None,
            "criado_em": criar_data_passada(2),
            "atualizado_em": criar_data_passada(2),
            "deleted_at": None
        },
        {
            "id": 5,
            "paciente_prep": encrypt_data("55502931"),
            "paciente_contato": None,
            "medico_solicitante_crm": "Dra. Ana Costa",
            "especialidade_id": 4,
            "sintomas_json": [{"id": 9, "nome": "Nódulo tireoidiano palpável"}],
            "gravidade": "VERDE",
            "status": "PENDENTE",
            "marcado_por": None,
            "data_consulta": None,
            "motivo_negacao": None,
            "criado_em": criar_data_passada(1),
            "atualizado_em": criar_data_passada(1),
            "deleted_at": None
        },
        {
            "id": 6,
            "paciente_prep": encrypt_data("66601928"),
            "paciente_contato": encrypt_data("(81) 95555-4444"),
            "medico_solicitante_crm": "Dra. Ana Costa",
            "especialidade_id": 1,
            "sintomas_json": [{"id": 12, "nome": "Convulsão"}],
            "gravidade": "VERMELHO",
            "status": "PENDENTE",
            "marcado_por": None,
            "data_consulta": None,
            "motivo_negacao": None,
            "criado_em": criar_data_passada(0),
            "atualizado_em": criar_data_passada(0),
            "deleted_at": None
        }
    ]
    
    with open(INTERCONSULTAS_JSON, mode="w", encoding="utf-8") as f:
        json.dump(interconsultas, f, indent=2, ensure_ascii=False)
        
    print(f"Interconsultas saved in {INTERCONSULTAS_JSON}")
    print("Database seeded successfully with realistic profiles!")

if __name__ == "__main__":
    main()

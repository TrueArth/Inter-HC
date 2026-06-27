from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from .resources.database import DatabaseManager, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")

    # Initialize AGHU DB Manager and store in app.state
    aghu_dsn = os.getenv("POSTGRES_DSN")
    if aghu_dsn:
        app.state.aghu_db = DatabaseManager(aghu_dsn)
        print("AGHU PostgreSQL connection pool initialized.")
    else:
        print("WARNING: POSTGRES_DSN not found. Skipping AGHU DB initialization.")

    # Initialize App DB Manager (SQLite) and store in app.state
    app_dsn = os.getenv("SQLITE_DSN")
    if not app_dsn:
        raise ValueError("SQLITE_DSN not found in environment variables.")
    app.state.app_db = DatabaseManager(app_dsn)
    print("App SQLite connection pool initialized.")

    # Create tables for App DB (if they don't exist) - for development only, Alembic handles this in production
    from .models.user import User
    from .models.interconsulta import InterconsultaPedido
    from .models.refresh_token import RefreshToken
    from .models.especialidade import Especialidade
    from .models.sintoma import Sintoma
    from .models.regra_gravidade import RegraGravidade
    from sqlalchemy import text
    import json    async with app.state.app_db.engine.begin() as conn:
        # Schema migration check: if sintomas table still has gravidade_padrao column, drop it and rules to update schema
        try:
            await conn.execute(text("SELECT gravidade_padrao FROM sintomas LIMIT 1"))
            print("Old schema detected. Dropping rules and symptoms tables to recreate with pontuacao...")
            await conn.execute(text("DROP TABLE IF EXISTS regras_gravidade"))
            await conn.execute(text("DROP TABLE IF EXISTS sintomas"))
        except Exception:
            pass

        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE interconsulta_pedidos ADD COLUMN marcado_por VARCHAR"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE interconsulta_pedidos ADD COLUMN data_consulta TIMESTAMP"))
        except Exception:
            pass
            
        # Seed specialties if table is empty
        res_esps = await conn.execute(text("SELECT COUNT(*) FROM especialidades WHERE deleted_at IS NULL"))
        esps_count = res_esps.scalar()
        if esps_count == 0:
            mock_esps = [
                {"id": 1, "nome": "Cardiologia"},
                {"id": 2, "nome": "Clínica Médica"},
                {"id": 3, "nome": "Dermatologia"},
                {"id": 4, "nome": "Endocrinologia"},
                {"id": 5, "nome": "Gastroenterologia"},
                {"id": 6, "nome": "Geriatria"},
                {"id": 7, "nome": "Hematologia"},
                {"id": 8, "nome": "Infectologia"},
                {"id": 9, "nome": "Medicina de Família e Comunidade"},
                {"id": 10, "nome": "Medicina do Trabalho"},
                {"id": 11, "nome": "Nefrologia"},
                {"id": 12, "nome": "Neurologia"},
                {"id": 13, "nome": "Oncologia (Alta Complexidade - CACON)"},
                {"id": 14, "nome": "Pediatria"},
                {"id": 15, "nome": "Pneumologia"},
                {"id": 16, "nome": "Psiquiatria"},
                {"id": 17, "nome": "Reumatologia"},
                {"id": 18, "nome": "Urologia"},
                {"id": 19, "nome": "Ginecologia e Obstetrícia"},
            ]
            stmt_esp = text(
                "INSERT INTO especialidades (id, nome, criado_em, atualizado_em) "
                "VALUES (:id, :nome, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
            for esp in mock_esps:
                await conn.execute(stmt_esp, esp)

        # Seed symptoms if table is empty or missing new ones
        mock_sints = [
            {"id": 1, "nome": "Cegueira / Perda súbita de visão", "pontuacao": 10},
            {"id": 2, "nome": "Infarto / Dor torácica súbita", "pontuacao": 10},
            {"id": 3, "nome": "AVC / Perda de força unilateral", "pontuacao": 10},
            {"id": 4, "nome": "Dor torácica intensa", "pontuacao": 5},
            {"id": 5, "nome": "Febre alta", "pontuacao": 5},
            {"id": 6, "nome": "Fratura", "pontuacao": 5},
            {"id": 7, "nome": "Ideação suicida ativa", "pontuacao": 5},
            {"id": 8, "nome": "Hematúria macroscópica", "pontuacao": 5},
            {"id": 9, "nome": "Nódulo tireoidiano palpável", "pontuacao": 1},
            {"id": 10, "nome": "Dispneia aguda", "pontuacao": 5},
            {"id": 11, "nome": "Dor abdominal intensa", "pontuacao": 5},
            {"id": 12, "nome": "Convulsão", "pontuacao": 5},
            {"id": 13, "nome": "Erupção cutânea com febre", "pontuacao": 1},
            {"id": 14, "nome": "Confusão mental aguda", "pontuacao": 1},
            {"id": 15, "nome": "Doença Renal Crônica estágio V", "pontuacao": 10},
            {"id": 16, "nome": "Síndrome Nefrótica grave (proteinúria > 8g/24h e/ou disfunção renal aguda)", "pontuacao": 10},
            {"id": 17, "nome": "Síndrome Nefrítica ou Glomerulonefrite rapidamente progressiva", "pontuacao": 10},
            {"id": 18, "nome": "Hipertensão arterial acelerada ou maligna", "pontuacao": 10},
            {"id": 19, "nome": "Injúria renal aguda", "pontuacao": 10},
            {"id": 20, "nome": "Alterações em sumário de urina com Injúria renal aguda", "pontuacao": 10},
            {"id": 21, "nome": "Doença Renal Crônica estágio IIIa a IV", "pontuacao": 5},
            {"id": 22, "nome": "Sinais/sintomas e alterações laboratoriais de DMO-DRC", "pontuacao": 5},
            {"id": 23, "nome": "DRC/dialítico com osteoporose e/ou fraturas", "pontuacao": 5},
            {"id": 24, "nome": "DRC/dialítico com hiperparatireoidismo secundário grave", "pontuacao": 5},
            {"id": 25, "nome": "Transplantado renal com osteoporose ou hiperparatireoidismo persistente", "pontuacao": 5},
            {"id": 26, "nome": "DRC de etiologia indeterminada com suspeita de causa genética/rara", "pontuacao": 5},
            {"id": 27, "nome": "Investigação de síndrome nefrótica ou nefrítica familiar", "pontuacao": 5},
            {"id": 28, "nome": "Distúrbio hidroeletrolítico de difícil diagnóstico e manejo", "pontuacao": 5},
            {"id": 29, "nome": "Investigação de nefrocalcinose sem causa definida", "pontuacao": 5},
            {"id": 30, "nome": "Síndrome Nefrótica leve a moderada (proteinúria < 8g/24h)", "pontuacao": 5},
            {"id": 31, "nome": "Hematúria isolada", "pontuacao": 2},
            {"id": 32, "nome": "Proteinúria subnefrótica isolada", "pontuacao": 2},
            {"id": 33, "nome": "Doença Renal Crônica estágio I ou II", "pontuacao": 2},
            {"id": 34, "nome": "Infecções urinárias complicadas (repetição e/ou rim único)", "pontuacao": 2},
        ]
        stmt_sint = text(
            "INSERT INTO sintomas (id, nome, pontuacao, criado_em, atualizado_em) "
            "VALUES (:id, :nome, :pontuacao, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
        for sint in mock_sints:
            res_exist = await conn.execute(text("SELECT 1 FROM sintomas WHERE id = :id"), {"id": sint["id"]})
            if not res_exist.scalar():
                await conn.execute(stmt_sint, sint)

        # Seed rules (overrides) if table is empty or missing new ones
        mock_rules = [
            {"sintoma_id": 4, "especialidade_id": 1, "pontuacao": 10},
            {"sintoma_id": 10, "especialidade_id": 1, "pontuacao": 10},
            {"sintoma_id": 2, "especialidade_id": 1, "pontuacao": 10}, # Infarto -> Cardiologia
            # Clínica Médica (ID 2)
            {"sintoma_id": 5, "especialidade_id": 2, "pontuacao": 5},
            {"sintoma_id": 12, "especialidade_id": 2, "pontuacao": 5},
            {"sintoma_id": 14, "especialidade_id": 2, "pontuacao": 1},
            # Dermatologia (ID 3)
            {"sintoma_id": 13, "especialidade_id": 3, "pontuacao": 5},
            {"sintoma_id": 9, "especialidade_id": 3, "pontuacao": 1},
            # Endocrinologia (ID 4)
            {"sintoma_id": 9, "especialidade_id": 4, "pontuacao": 5},
            {"sintoma_id": 5, "especialidade_id": 4, "pontuacao": 5},
            # Gastroenterologia (ID 5)
            {"sintoma_id": 11, "especialidade_id": 5, "pontuacao": 10},
            {"sintoma_id": 10, "especialidade_id": 5, "pontuacao": 5},
            # Geriatria (ID 6)
            {"sintoma_id": 14, "especialidade_id": 6, "pontuacao": 5},
            {"sintoma_id": 7, "especialidade_id": 6, "pontuacao": 5},
            # Hematologia (ID 7)
            {"sintoma_id": 8, "especialidade_id": 7, "pontuacao": 5},
            {"sintoma_id": 5, "especialidade_id": 7, "pontuacao": 5},
            # Infectologia (ID 8)
            {"sintoma_id": 5, "especialidade_id": 8, "pontuacao": 5},
            {"sintoma_id": 13, "especialidade_id": 8, "pontuacao": 5},
            # Medicina de Família e Comunidade (ID 9)
            {"sintoma_id": 1, "especialidade_id": 9, "pontuacao": 10},
            {"sintoma_id": 4, "especialidade_id": 9, "pontuacao": 5},
            {"sintoma_id": 5, "especialidade_id": 9, "pontuacao": 5},
            {"sintoma_id": 6, "especialidade_id": 9, "pontuacao": 5},
            # Medicina do Trabalho (ID 10)
            {"sintoma_id": 4, "especialidade_id": 10, "pontuacao": 5},
            {"sintoma_id": 14, "especialidade_id": 10, "pontuacao": 1},
            # Nefrologia (ID 11)
            {"sintoma_id": 8, "especialidade_id": 11, "pontuacao": 10},
            # Novas regras da Nefrologia (ID 11)
            {"sintoma_id": 15, "especialidade_id": 11, "pontuacao": 10},
            {"sintoma_id": 16, "especialidade_id": 11, "pontuacao": 10},
            {"sintoma_id": 17, "especialidade_id": 11, "pontuacao": 10},
            {"sintoma_id": 18, "especialidade_id": 11, "pontuacao": 10},
            {"sintoma_id": 19, "especialidade_id": 11, "pontuacao": 10},
            {"sintoma_id": 20, "especialidade_id": 11, "pontuacao": 10},
            {"sintoma_id": 21, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 22, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 23, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 24, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 25, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 26, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 27, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 28, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 29, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 30, "especialidade_id": 11, "pontuacao": 5},
            {"sintoma_id": 31, "especialidade_id": 11, "pontuacao": 2},
            {"sintoma_id": 32, "especialidade_id": 11, "pontuacao": 2},
            {"sintoma_id": 33, "especialidade_id": 11, "pontuacao": 2},
            {"sintoma_id": 34, "especialidade_id": 11, "pontuacao": 2},
            # Neurologia (ID 12)
            {"sintoma_id": 12, "especialidade_id": 12, "pontuacao": 10},
            {"sintoma_id": 14, "especialidade_id": 12, "pontuacao": 5},
            # Oncologia (ID 13)
            {"sintoma_id": 9, "especialidade_id": 13, "pontuacao": 5},
            # Pediatria (ID 14)
            {"sintoma_id": 5, "especialidade_id": 14, "pontuacao": 5},
            {"sintoma_id": 12, "especialidade_id": 14, "pontuacao": 10},
            # Pneumologia (ID 15)
            {"sintoma_id": 10, "especialidade_id": 15, "pontuacao": 10},
            # Psiquiatria (ID 16)
            {"sintoma_id": 7, "especialidade_id": 16, "pontuacao": 10},
            # Reumatologia (ID 17)
            {"sintoma_id": 6, "especialidade_id": 17, "pontuacao": 5},
            # Urologia (ID 18)
            {"sintoma_id": 8, "especialidade_id": 18, "pontuacao": 10},
            # Ginecologia e Obstetrícia (ID 19)
            {"sintoma_id": 11, "especialidade_id": 19, "pontuacao": 5},
            {"sintoma_id": 5, "especialidade_id": 19, "pontuacao": 5},
        ]
        stmt_rule = text(
            "INSERT INTO regras_gravidade (sintoma_id, especialidade_id, pontuacao, criado_em, atualizado_em) "
            "VALUES (:sintoma_id, :especialidade_id, :pontuacao, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
        for rule in mock_rules:
            res_exist = await conn.execute(
                text("SELECT 1 FROM regras_gravidade WHERE sintoma_id = :sintoma_id AND especialidade_id = :especialidade_id"),
                {"sintoma_id": rule["sintoma_id"], "especialidade_id": rule["especialidade_id"]}
            )
            if not res_exist.scalar():
                await conn.execute(stmt_rule, rule)
            
        # Seed users if users table is empty
        res_users = await conn.execute(text("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL"))
        users_count = res_users.scalar()
        if users_count == 0:
            from src.helpers.crypto_helper import hash_password
            mock_users = [
                {"username": "admin", "pwd": hash_password("admin"), "name": "Administrador do Sistema", "role": "admin", "email": "admin@ufpe.br"},
                {"username": "medico", "pwd": hash_password("medico"), "name": "Dr. Carlos Silva", "role": "medico", "email": "carlos.silva@ufpe.br"},
                {"username": "regulador", "pwd": hash_password("regulador"), "name": "Regulador Central", "role": "regulador", "email": "regulador@ufpe.br"},
                {"username": "medico2", "pwd": hash_password("medico2"), "name": "Dra. Ana Costa", "role": "medico", "email": "ana.costa@ufpe.br"},
                {"username": "medico3", "pwd": hash_password("medico3"), "name": "Dr. Roberto Souza", "role": "medico", "email": "roberto.souza@ufpe.br"},
            ]
            stmt_user = text(
                "INSERT INTO users (username, hashed_password, display_name, role, email, created_at, updated_at) "
                "VALUES (:username, :pwd, :name, :role, :email, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
            for u in mock_users:
                await conn.execute(stmt_user, u)
                
        # Seed interconsultas if empty
        res_pedidos = await conn.execute(text("SELECT COUNT(*) FROM interconsulta_pedidos WHERE deleted_at IS NULL"))
        pedidos_count = res_pedidos.scalar()
        if pedidos_count == 0:
            from src.helpers.crypto_helper import encrypt_data
            mock_pedidos = [
                {"prep": encrypt_data("10000016"), "medico": "Dr. Carlos Silva", "esp_id": 1, "sintomas": json.dumps([{"id": 4, "nome": "Dor torácica intensa"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"prep": encrypt_data("7700201"), "medico": "Dr. Carlos Silva", "esp_id": 1, "sintomas": json.dumps([{"id": 2, "nome": "Infarto / Dor torácica súbita"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"prep": encrypt_data("7700301"), "medico": "Dr. Roberto Souza", "esp_id": 2, "sintomas": json.dumps([{"id": 14, "nome": "Confusão mental aguda"}]), "gravidade": "AMARELO", "status": "PENDENTE"},
                {"prep": encrypt_data("7700401"), "medico": "Dr. Roberto Souza", "esp_id": 3, "sintomas": json.dumps([{"id": 6, "nome": "Fratura"}]), "gravidade": "VERDE", "status": "PENDENTE"},
                {"prep": encrypt_data("55555555"), "medico": "Dr. Roberto Souza", "esp_id": 4, "sintomas": json.dumps([{"id": 9, "nome": "Nódulo tireoidiano palpável"}]), "gravidade": "VERDE", "status": "PENDENTE"},
                {"prep": encrypt_data("66666666"), "medico": "Dra. Ana Costa", "esp_id": 12, "sintomas": json.dumps([{"id": 12, "nome": "Convulsão"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"prep": encrypt_data("77777777"), "medico": "Dra. Ana Costa", "esp_id": 1, "sintomas": json.dumps([{"id": 10, "nome": "Dispneia aguda"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"prep": encrypt_data("88888888"), "medico": "Dra. Ana Costa", "esp_id": 2, "sintomas": json.dumps([{"id": 5, "nome": "Febre alta"}]), "gravidade": "AMARELO", "status": "PENDENTE"},
            ]
            stmt_pedido = text(
                "INSERT INTO interconsulta_pedidos (paciente_prep, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, criado_em, atualizado_em) "
                "VALUES (:prep, :medico, :esp_id, :sintomas, :gravidade, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
            for p in mock_pedidos:
                await conn.execute(stmt_pedido, p)
    print("App SQLite tables checked/created.")

    # Seed mock JSON files if they don't exist or are empty (Offline development mode)
    try:
        from datetime import timezone
        from src.helpers.crypto_helper import hash_password, encrypt_data
        
        users_json_path = "data/users.json"
        if not os.path.exists(users_json_path) or os.path.getsize(users_json_path) == 0:
            os.makedirs(os.path.dirname(users_json_path), exist_ok=True)
            from datetime import datetime
            default_users = [
                {"id": 1, "username": "admin", "hashed_password": hash_password("admin"), "display_name": "Administrador do Sistema", "role": "admin", "email": "admin@ufpe.br", "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat(), "deleted_at": None},
                {"id": 2, "username": "medico", "hashed_password": hash_password("medico"), "display_name": "Dr. Carlos Silva", "role": "medico", "email": "carlos.silva@ufpe.br", "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat(), "deleted_at": None},
                {"id": 3, "username": "regulador", "hashed_password": hash_password("regulador"), "display_name": "Regulador Central", "role": "regulador", "email": "regulador@ufpe.br", "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat(), "deleted_at": None},
                {"id": 4, "username": "medico2", "hashed_password": hash_password("medico2"), "display_name": "Dra. Ana Costa", "role": "medico", "email": "ana.costa@ufpe.br", "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat(), "deleted_at": None},
                {"id": 5, "username": "medico3", "hashed_password": hash_password("medico3"), "display_name": "Dr. Roberto Souza", "role": "medico", "email": "roberto.souza@ufpe.br", "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat(), "deleted_at": None}
            ]
            with open(users_json_path, "w", encoding="utf-8") as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
            print("Mock JSON users database seeded.")

        interconsultas_json_path = "data/interconsultas.json"
        if not os.path.exists(interconsultas_json_path) or os.path.getsize(interconsultas_json_path) == 0:
            os.makedirs(os.path.dirname(interconsultas_json_path), exist_ok=True)
            from datetime import datetime
            now_str = datetime.now(timezone.utc).isoformat()
            default_pedidos = [
                {"id": 1, "paciente_prep": encrypt_data("10000016"), "medico_solicitante_crm": "Dr. Carlos Silva", "especialidade_id": 1, "sintomas_json": [{"id": 4, "nome": "Dor torácica intensa"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 2, "paciente_prep": encrypt_data("7700201"), "medico_solicitante_crm": "Dr. Carlos Silva", "especialidade_id": 1, "sintomas_json": [{"id": 2, "nome": "Infarto / Dor torácica súbita"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 3, "paciente_prep": encrypt_data("7700301"), "medico_solicitante_crm": "Dr. Roberto Souza", "especialidade_id": 2, "sintomas_json": [{"id": 14, "nome": "Confusão mental aguda"}], "gravidade": "AMARELO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 4, "paciente_prep": encrypt_data("7700401"), "medico_solicitante_crm": "Dr. Roberto Souza", "especialidade_id": 3, "sintomas_json": [{"id": 6, "nome": "Fratura"}], "gravidade": "VERDE", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 5, "paciente_prep": encrypt_data("55555555"), "medico_solicitante_crm": "Dr. Roberto Souza", "especialidade_id": 4, "sintomas_json": [{"id": 9, "nome": "Nódulo tireoidiano palpável"}], "gravidade": "VERDE", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 6, "paciente_prep": encrypt_data("66666666"), "medico_solicitante_crm": "Dra. Ana Costa", "especialidade_id": 12, "sintomas_json": [{"id": 12, "nome": "Convulsão"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 7, "paciente_prep": encrypt_data("77777777"), "medico_solicitante_crm": "Dra. Ana Costa", "especialidade_id": 1, "sintomas_json": [{"id": 10, "nome": "Dispneia aguda"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 8, "paciente_prep": encrypt_data("88888888"), "medico_solicitante_crm": "Dra. Ana Costa", "especialidade_id": 2, "sintomas_json": [{"id": 5, "nome": "Febre alta"}], "gravidade": "AMARELO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None}
            ]
            with open(interconsultas_json_path, "w", encoding="utf-8") as f:
                json.dump(default_pedidos, f, indent=2, ensure_ascii=False)
            print("Mock JSON interconsultas database seeded.")
    except Exception as e:
        print(f"Error seeding mock JSON files: {e}")

    yield

    # Shutdown
    print("Shutting down...")
    if hasattr(app.state, 'aghu_db') and app.state.aghu_db:
        await app.state.aghu_db.close_connection()
        print("AGHU PostgreSQL connection pool closed.")
    if hasattr(app.state, 'app_db') and app.state.app_db:
        await app.state.app_db.close_connection()
        print("App SQLite connection pool closed.")

app = FastAPI(
    title="Esqueleto de Aplicação Web Full-Stack",
    description="Aplicação Backend monolítica (API REST) em Python/FastAPI, com foco em acesso e agregação de dados heterogêneos.",
    version="1.0.0",
    lifespan=lifespan,
)

# Serve o frontend Vue 3 empacotado
app.mount("/static/dist/assets", StaticFiles(directory="src/static/dist/assets"), name="assets")
app.mount("/static/dist", StaticFiles(directory="src/static/dist"), name="static")

# Placeholder para incluir os roteadores da API
from .routers import paciente, auth, admin, aih, bpa, material, interconsulta
app.include_router(paciente.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(aih.router)
app.include_router(bpa.router)
app.include_router(material.router)
app.include_router(interconsulta.router)

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve o arquivo index.html para todas as rotas que não são da API ou arquivos estáticos.
    Isso é necessário para que o roteamento do Vue (SPA) funcione.
    """
    # Se a rota começa com 'api', deixa o roteador do FastAPI lidar
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    index_path = os.path.join("src", "static", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build not found"}

# Exemplo:
# from .routers import aih, bpa, material
# app.include_router(aih.router)
# app.include_router(bpa.router)
# app.include_router(material.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

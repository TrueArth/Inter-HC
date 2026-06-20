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
    from sqlalchemy import text
    import json
    async with app.state.app_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE interconsulta_pedidos ADD COLUMN marcado_por VARCHAR"))
        except Exception:
            pass
            
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
                {"cns": encrypt_data("111111111111111"), "medico": "Dr. Carlos Silva", "esp_id": 1, "sintomas": json.dumps([{"id": 4, "nome": "Dor torácica intensa"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"cns": encrypt_data("222222222222222"), "medico": "Dr. Carlos Silva", "esp_id": 1, "sintomas": json.dumps([{"id": 2, "nome": "Infarto / Dor torácica súbita"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"cns": encrypt_data("333333333333333"), "medico": "Dr. Roberto Souza", "esp_id": 2, "sintomas": json.dumps([{"id": 14, "nome": "Confusão mental aguda"}]), "gravidade": "AMARELO", "status": "PENDENTE"},
                {"cns": encrypt_data("444444444444444"), "medico": "Dr. Roberto Souza", "esp_id": 3, "sintomas": json.dumps([{"id": 6, "nome": "Fratura"}]), "gravidade": "VERDE", "status": "PENDENTE"},
                {"cns": encrypt_data("555555555555555"), "medico": "Dr. Roberto Souza", "esp_id": 4, "sintomas": json.dumps([{"id": 9, "nome": "Nódulo tireoidiano palpável"}]), "gravidade": "VERDE", "status": "PENDENTE"},
                {"cns": encrypt_data("666666666666666"), "medico": "Dra. Ana Costa", "esp_id": 12, "sintomas": json.dumps([{"id": 12, "nome": "Convulsão"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"cns": encrypt_data("777777777777777"), "medico": "Dra. Ana Costa", "esp_id": 1, "sintomas": json.dumps([{"id": 10, "nome": "Dispneia aguda"}]), "gravidade": "VERMELHO", "status": "PENDENTE"},
                {"cns": encrypt_data("888888888888888"), "medico": "Dra. Ana Costa", "esp_id": 2, "sintomas": json.dumps([{"id": 5, "nome": "Febre alta"}]), "gravidade": "AMARELO", "status": "PENDENTE"},
            ]
            stmt_pedido = text(
                "INSERT INTO interconsulta_pedidos (paciente_cns, medico_solicitante_crm, especialidade_id, sintomas_json, gravidade, status, criado_em, atualizado_em) "
                "VALUES (:cns, :medico, :esp_id, :sintomas, :gravidade, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
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
                {"id": 1, "paciente_cns": encrypt_data("111111111111111"), "medico_solicitante_crm": "Dr. Carlos Silva", "especialidade_id": 1, "sintomas_json": [{"id": 4, "nome": "Dor torácica intensa"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 2, "paciente_cns": encrypt_data("222222222222222"), "medico_solicitante_crm": "Dr. Carlos Silva", "especialidade_id": 1, "sintomas_json": [{"id": 2, "nome": "Infarto / Dor torácica súbita"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 3, "paciente_cns": encrypt_data("333333333333333"), "medico_solicitante_crm": "Dr. Roberto Souza", "especialidade_id": 2, "sintomas_json": [{"id": 14, "nome": "Confusão mental aguda"}], "gravidade": "AMARELO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 4, "paciente_cns": encrypt_data("444444444444444"), "medico_solicitante_crm": "Dr. Roberto Souza", "especialidade_id": 3, "sintomas_json": [{"id": 6, "nome": "Fratura"}], "gravidade": "VERDE", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 5, "paciente_cns": encrypt_data("555555555555555"), "medico_solicitante_crm": "Dr. Roberto Souza", "especialidade_id": 4, "sintomas_json": [{"id": 9, "nome": "Nódulo tireoidiano palpável"}], "gravidade": "VERDE", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 6, "paciente_cns": encrypt_data("666666666666666"), "medico_solicitante_crm": "Dra. Ana Costa", "especialidade_id": 12, "sintomas_json": [{"id": 12, "nome": "Convulsão"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 7, "paciente_cns": encrypt_data("777777777777777"), "medico_solicitante_crm": "Dra. Ana Costa", "especialidade_id": 1, "sintomas_json": [{"id": 10, "nome": "Dispneia aguda"}], "gravidade": "VERMELHO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None},
                {"id": 8, "paciente_cns": encrypt_data("888888888888888"), "medico_solicitante_crm": "Dra. Ana Costa", "especialidade_id": 2, "sintomas_json": [{"id": 5, "nome": "Febre alta"}], "gravidade": "AMARELO", "status": "PENDENTE", "marcado_por": None, "criado_em": now_str, "atualizado_em": now_str, "deleted_at": None}
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

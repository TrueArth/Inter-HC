from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ..auth.auth import auth_handler
from ..dependencies import get_user_provider, get_interconsulta_provider
from ..controllers.user_controller import UserController


router = APIRouter(prefix="/api", tags=["Admin"])

# --- Schemas ---

class AdminData(BaseModel):
    message: str
    user_groups: List[str]

class UserCreate(BaseModel):
    username: str = Field(..., description="Nome de usuário para login")
    password: str = Field(..., description="Senha do usuário")
    display_name: str = Field(..., description="Nome de exibição")
    role: str = Field(..., description="Papel: admin, medico ou regulador")
    email: Optional[str] = Field(None, description="Endereço de e-mail")

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, description="Nome de exibição")
    role: Optional[str] = Field(None, description="Papel: admin, medico ou regulador")
    email: Optional[str] = Field(None, description="Endereço de e-mail")

class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Dependências ---

async def verify_admin_group(current_user: dict = Depends(auth_handler.decode_token)):
    ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"
    role = current_user.get("role")
    if role:
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acesso negado: Operação restrita ao Administrador."
            )
    else:
        if ADMIN_GROUP not in current_user.get("groups", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acesso negado: Privilégios insuficientes."
            )
    return current_user

# --- Endpoints ---

@router.get("/admin-only-data", response_model=AdminData)
async def get_admin_data(current_user: dict = Depends(verify_admin_group)):
    """
    Retorna dados confidenciais apenas acessíveis por administradores.
    """
    return AdminData(
        message="This is highly confidential admin data!",
        user_groups=current_user.get("groups", [])
    )

@router.get("/admin/users", response_model=List[UserResponse])
async def get_users(
    provider = Depends(get_user_provider()),
    current_user = Depends(verify_admin_group)
):
    """
    Retorna a lista de usuários cadastrados no banco de dados local.
    """
    return await UserController.listar_usuarios(provider)

@router.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    provider = Depends(get_user_provider()),
    current_user = Depends(verify_admin_group)
):
    """
    Cria um novo usuário local no banco de dados.
    """
    return await UserController.criar_usuario(payload.dict(), provider)

@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    provider = Depends(get_user_provider()),
    current_user = Depends(verify_admin_group)
):
    """
    Atualiza as informações de um usuário local.
    """
    return await UserController.atualizar_usuario(user_id, payload.dict(exclude_unset=True), provider)

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    provider = Depends(get_user_provider()),
    current_user = Depends(verify_admin_group)
):
    """
    Desativa um usuário local (Soft Delete).
    """
    return await UserController.cancelar_usuario(user_id, provider)


class SpecialtyStat(BaseModel):
    name: str
    count: int


class DoctorStat(BaseModel):
    name: str
    count: int


class AdminStatistics(BaseModel):
    top_specialty: SpecialtyStat
    specialties_distribution: List[SpecialtyStat]
    top_doctors: List[DoctorStat]
    inappropriate_doctors: List[DoctorStat]


@router.get("/admin/statistics", response_model=AdminStatistics)
async def get_admin_statistics(
    interconsulta_provider = Depends(get_interconsulta_provider()),
    current_user = Depends(verify_admin_group)
):
    """
    Retorna estatísticas para o dashboard administrativo.
    """
    from collections import Counter
    
    # Busca todas as interconsultas ativas (onde deleted_at IS NULL)
    pedidos = await interconsulta_provider.listar_pedidos_ativos()
    
    # Dicionário de mapeamento de especialidades
    especialidades_map = {
        1: 'Cardiologia',
        2: 'Clínica Médica',
        3: 'Dermatologia',
        4: 'Endocrinologia',
        5: 'Gastroenterologia',
        6: 'Geriatria',
        7: 'Hematologia',
        8: 'Infectologia',
        9: 'Medicina de Família e Comunidade',
        10: 'Medicina do Trabalho',
        11: 'Nefrologia',
        12: 'Neurologia',
        13: 'Oncologia (Alta Complexidade - CACON)',
        14: 'Pediatria',
        15: 'Pneumologia',
        16: 'Psiquiatria',
        17: 'Reumatologia',
        18: 'Urologia',
        19: 'Ginecologia e Obstetrícia',
    }
    
    specialties_counter = Counter()
    doctors_counter = Counter()
    indevidas_counter = Counter()
    
    for p in pedidos:
        esp_id = p.get("especialidade_id")
        esp_name = especialidades_map.get(esp_id, f"Especialidade {esp_id}")
        specialties_counter[esp_name] += 1
        
        medico = p.get("medico_solicitante_crm") or "Desconhecido"
        doctors_counter[medico] += 1
        
        gravidade = p.get("gravidade", "VERDE").upper()
        if gravidade == "VERDE":
            indevidas_counter[medico] += 1
            
    # Formata retornos
    top_specialty_item = specialties_counter.most_common(1)
    top_specialty = {
        "name": top_specialty_item[0][0],
        "count": top_specialty_item[0][1]
    } if top_specialty_item else {"name": "Nenhuma", "count": 0}
    
    specialties_distribution = [
        {"name": k, "count": v} for k, v in specialties_counter.most_common()
    ]
    top_doctors = [
        {"name": k, "count": v} for k, v in doctors_counter.most_common()
    ]
    inappropriate_doctors = [
        {"name": k, "count": v} for k, v in indevidas_counter.most_common()
    ]
    
    return {
        "top_specialty": top_specialty,
        "specialties_distribution": specialties_distribution,
        "top_doctors": top_doctors,
        "inappropriate_doctors": inappropriate_doctors
    }


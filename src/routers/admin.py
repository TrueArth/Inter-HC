from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ..auth.auth import auth_handler
from ..dependencies import get_user_provider
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

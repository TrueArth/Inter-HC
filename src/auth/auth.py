import os
import jwt
from ldap3 import Server, Connection, ALL, SUBTREE, SIMPLE
import re
import secrets
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..resources.database import get_app_db_session
from ..models.refresh_token import RefreshToken

load_dotenv()

# --- Configurações --- 
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 24))
REFRESH_TOKEN_EXP_DAYS = int(os.getenv("REFRESH_TOKEN_EXP_DAYS", 30))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# --- Interface e Implementações de Provedor de Autenticação ---

class AuthProviderInterface(ABC):
    """Interface para provedores de autenticação."""
    @abstractmethod
    async def authenticate_user(self, username, password, db=None) -> dict:
        pass

class MockAuthProvider(AuthProviderInterface):
    """Provedor de autenticação mock para desenvolvimento offline, integrado com banco local."""
    async def authenticate_user(self, username, password, db=None) -> dict:
        print("--- Authenticating with MockAuthProvider ---")
        
        # 1. Tentativa de autenticação no banco local se o banco estiver presente
        if db is not None:
            try:
                from ..helpers.crypto_helper import verify_password
                from ..providers.implementations.user_postgres_provider import UserPostgresProvider
                
                dialect = db.bind.dialect.name if db.bind else "postgresql"
                provider = UserPostgresProvider(session=db, dialect=dialect)
                
                # Se a tabela de usuários estiver vazia, cria o admin inicial
                usuarios = await provider.listar_usuarios()
                if not usuarios:
                    from ..helpers.crypto_helper import hash_password
                    admin_initial = {
                        "username": "admin",
                        "hashed_password": hash_password("admin"),
                        "display_name": "Administrador do Sistema",
                        "role": "admin",
                        "email": "admin@ufpe.br"
                    }
                    await provider.inserir_usuario(admin_initial)
                
                user_db = await provider.buscar_usuario_por_username(username)
                if user_db:
                    # Se password for None, estamos re-autenticando no refresh, aceita
                    if password is None or verify_password(password, user_db["hashed_password"]):
                        admin_group = "GLO-SEC-HCPE-SETISD"
                        role = user_db["role"]
                        groups = ["Users"]
                        if role == "admin":
                            groups.extend([admin_group, "Medicos"])
                        elif role == "medico":
                            groups.append("Medicos")
                        elif role == "regulador":
                            groups.append("Reguladores")
                            
                        return {
                            "username": user_db["username"],
                            "displayName": [user_db["display_name"]],
                            "name": user_db["display_name"],
                            "groups": groups,
                            "role": role,
                            "email": user_db.get("email") or ""
                        }
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Credenciais inválidas no banco de dados local"
                        )
            except HTTPException:
                raise
            except Exception as e:
                print(f"Erro na autenticação local do banco (continuando para fallback): {e}")
                
        # 2. Fallback para usuários mock estáticos (compatibilidade de teste e desenvolvimento)
        print("--- Using Static Mock Fallback ---")
        admin_group = "GLO-SEC-HCPE-SETISD"
        if username == "admin" and (password is None or password == "admin"):
            return {
                "username": "admin",
                "displayName": ["Mock Admin"],
                "name": "Mock Admin",
                "groups": [admin_group, "Medicos", "Users"],
                "role": "admin",
                "email": "admin@mock.com"
            }
        elif username == "medico" and (password is None or password == "medico"):
            return {
                "username": "medico",
                "displayName": ["Mock Medico"],
                "name": "Mock Medico",
                "groups": ["Medicos", "Users"],
                "role": "medico",
                "email": "medico@mock.com"
            }
        elif username == "regulador" and (password is None or password == "regulador"):
            return {
                "username": "regulador",
                "displayName": ["Mock Regulador"],
                "name": "Mock Regulador",
                "groups": ["Reguladores", "Users"],  # Reguladores apenas!
                "role": "regulador",
                "email": "regulador@mock.com"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Credenciais inválidas"
            )

class ActiveDirectoryAuthProvider(AuthProviderInterface):
    """Provedor de autenticação real usando LDAP/Active Directory (ldap3)."""
    def __init__(self):
        self.ad_url = os.getenv("AD_URL")
        self.ad_basedn = os.getenv("AD_BASEDN")
        self.ad_bind_user = os.getenv("AD_BIND_USER")
        self.ad_bind_password = os.getenv("AD_BIND_PASSWORD")
        if not self.ad_url or not self.ad_basedn:
            raise RuntimeError("Active Directory is not configured. Check .env file.")

    async def authenticate_user(self, username, password, db=None) -> dict:
        print(f"--- Starting AD Authentication (ldap3) for user: {username} ---")
        try:
            server = Server(self.ad_url, get_info=ALL)
            user_bind_dn = f"EBSERHNET\\{username}"
            
            # Autenticação inicial (Bind)
            conn = Connection(server, user=user_bind_dn, password=password, authentication=SIMPLE, check_names=True, raise_exceptions=True)
            conn.bind()

            # Se chegamos aqui, o bind foi bem sucedido.
            # Agora buscamos informações do usuário e seus grupos.
            search_conn = conn
            if self.ad_bind_user and self.ad_bind_password:
                # Opcional: usar um usuário de serviço para buscas se o usuário logado tiver restrições
                search_conn = Connection(server, user=self.ad_bind_user, password=self.ad_bind_password, authentication=SIMPLE, check_names=True, raise_exceptions=True)
                search_conn.bind()

            search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
            search_conn.search(self.ad_basedn, search_filter, search_scope=SUBTREE, attributes=['*'])

            if not search_conn.entries:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User found during bind but search returned no data.")

            user_entry = search_conn.entries[0]
            user_info = {"username": username}
            groups = []

            # Extração de atributos selecionados para evitar problemas de serialização (como datetime)
            allowed_attrs = {
                'displayName': 'displayName',
                'mail': 'email',
                'title': 'title',
                'department': 'department',
                'employeeNumber': 'employeeNumber',
                'givenName': 'givenName',
                'userPrincipalName': 'userPrincipalName'
            }
            
            for attr_name in user_entry.entry_attributes:
                value = user_entry[attr_name].value
                attr_lower = attr_name.lower()
                
                if attr_lower == 'memberof':
                    raw_groups = value if isinstance(value, list) else [value]
                    for group_dn in raw_groups:
                        match = re.match(r'CN=([^,]+)', group_dn)
                        if match:
                            groups.append(match.group(1))
                    user_info['groups'] = groups
                elif attr_name in allowed_attrs:
                    # Garante que o valor seja SEMPRE uma lista de strings para o frontend
                    if isinstance(value, list):
                        user_info[allowed_attrs[attr_name]] = [str(v) for v in value]
                    else:
                        user_info[allowed_attrs[attr_name]] = [str(value)] if value is not None else []

            # Garante que groups sempre exista
            if 'groups' not in user_info:
                user_info['groups'] = []

            # Limpeza das conexões
            if search_conn != conn:
                search_conn.unbind()
            conn.unbind()
            
            print(f"--- AD Authentication successful for user: {username}. ---")
            return user_info

        except Exception as e:
            # Tratamento de erros específicos do ldap3 ou genéricos
            error_str = str(e)
            if "invalidCredentials" in error_str:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            elif "server not available" in error_str.lower():
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AD server is down or unreachable")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AD error: {e}")

# --- AuthHandler Principal ---

class AuthHandler:
    def __init__(self):
        # Lógica de troca: decide qual provedor usar na inicialização
        if os.getenv("AD_URL"):
            print("INFO: Using Active Directory authentication.")
            self.provider: AuthProviderInterface = ActiveDirectoryAuthProvider()
        else:
            print("WARNING: AD environment variables not found. Using Mock authentication.")
            self.provider: AuthProviderInterface = MockAuthProvider()

    async def authenticate_user(self, username, password, db=None):
        return await self.provider.authenticate_user(username, password, db=db)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if 'username' in to_encode:
            to_encode['sub'] = to_encode['username']
        
        # Use o tempo Unix (timestamp) para garantir serialização JSON
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=JWT_EXP_HOURS))
        to_encode.update({"exp": int(expire.timestamp())})
        
        if not JWT_SECRET:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT_SECRET not configured")
        return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

    async def create_refresh_token(self, user_id: str, groups: list, db: AsyncSession) -> str:
        refresh_token_string = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXP_DAYS)
        new_refresh_token = RefreshToken(user_id=user_id, token=refresh_token_string, groups=groups, expires_at=expires_at)
        db.add(new_refresh_token)
        await db.commit()
        return refresh_token_string

    async def verify_refresh_token(self, refresh_token: str, db: AsyncSession):
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token)
        result = await db.execute(stmt)
        token_obj = result.scalar_one_or_none()
        if not token_obj or token_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        return token_obj

    async def invalidate_refresh_token(self, refresh_token: str, db: AsyncSession):
        stmt = delete(RefreshToken).where(RefreshToken.token == refresh_token)
        await db.execute(stmt)
        await db.commit()

    def decode_token(self, token: str = Depends(oauth2_scheme)):
        try:
            if not JWT_SECRET:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT_SECRET not configured")
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Instância única que será usada em toda a aplicação
auth_handler = AuthHandler()
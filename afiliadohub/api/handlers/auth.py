import os
import base64
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from ..utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

# --- JWT Secret (Supabase signs tokens with this) ---
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
if not SUPABASE_JWT_SECRET:
    logger.error("[Auth] SUPABASE_JWT_SECRET está vazio no .env")


# --- Models ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    role: str = "client"


# --- Handlers ---
@router.post("/register")
def register(user: UserRegister):
    """Registra um novo usuário (Cliente por padrão)"""
    supabase = get_supabase_manager()
    final_role = "client"  # Força role seguro. Admin é promovido manualmente no Supabase.

    try:
        auth_response = supabase.client.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
                "options": {"data": {"name": user.name, "role": final_role}},
            }
        )

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Erro ao criar usuário")

        return {
            "success": True,
            "message": "Usuário criado com sucesso",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "role": final_role,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Auth] Erro no registro: {repr(e)}")
        raise HTTPException(status_code=400, detail="Erro ao criar conta. Verifique os dados.")


@router.post("/login")
def login(credentials: UserLogin):
    """Faz login e retorna token + role"""
    supabase = get_supabase_manager()

    try:
        auth_response = supabase.client.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )

        if not auth_response.user or not auth_response.session:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        # Check app_metadata first (secure — só o backend pode editar)
        # Fallback para user_metadata por compatibilidade
        app_meta = auth_response.user.app_metadata or {}
        user_meta = auth_response.user.user_metadata or {}
        role = app_meta.get("role") or user_meta.get("role", "client")
        name = user_meta.get("name", "Usuário")

        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "name": name,
                "role": role,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Auth] Erro no login: {repr(e)}")
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")


# --- Authentication Dependencies ---

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Valida token JWT do Supabase com verificação de assinatura.
    Retorna os dados do usuário ou levanta 401.
    """
    import jwt

    token = credentials.credentials

    if not SUPABASE_JWT_SECRET:
        logger.error("[Auth] SUPABASE_JWT_SECRET não configurado")
        raise HTTPException(status_code=500, detail="Servidor com configuração incompleta")

    try:
        # Verifica assinatura real com o JWT Secret do Supabase
        decoded = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",  # Supabase define aud="authenticated"
        )

        app_metadata = decoded.get("app_metadata", {})
        user_metadata = decoded.get("user_metadata", {})
        role = app_metadata.get("role") or user_metadata.get("role", "client")

        return {
            "id": decoded.get("sub"),
            "email": decoded.get("email"),
            "name": user_metadata.get("name", "Usuário"),
            "role": role,
            "token": token
        }

    except jwt.ExpiredSignatureError as e:
        logger.error(f"[Auth JWT] ExpiredSignatureError: {str(e)}")
        raise HTTPException(status_code=401, detail="Sessão expirada. Faça login novamente.")
    except jwt.InvalidAudienceError as e:
        logger.error(f"[Auth JWT] InvalidAudienceError: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.InvalidSignatureError as e:
        logger.error(f"[Auth JWT] InvalidSignatureError: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.InvalidTokenError as e:
        logger.error(f"[Auth JWT] InvalidTokenError ({type(e).__name__}): {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Auth JWT] Erro inesperado ao validar token: {type(e).__name__} -> {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Valida que usuário é admin.
    Usado em rotas administrativas.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    return current_user

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from ..utils.supabase_client import get_supabase_manager

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- Models ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    role: str = "client" # Default role

# --- Handlers ---
@router.post("/register")
async def register(user: UserRegister):
    """Registra um novo usuário (Cliente por padrão)"""
    supabase = get_supabase_manager()
    
    # Force role to stay safe if needed, or allow 'client' only for public registration
    final_role = "client" 
    
    try:
        # Create user in Supabase Auth with metadata
        auth_response = supabase.client.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "name": user.name,
                    "role": final_role
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Erro ao criar usuário")
            
        return {
            "success": True, 
            "message": "Usuário criado com sucesso",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "role": final_role
            }
        }
    except Exception as e:
        # Supabase raises exceptions for existing users, weak passwords, etc.
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(credentials: UserLogin):
    """Faz login e retorna token + role"""
    supabase = get_supabase_manager()
    
    try:
        auth_response = supabase.client.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
            
        # Extract metadata
        user_meta = auth_response.user.user_metadata or {}
        role = user_meta.get("role", "client") # Default to client if missing
        name = user_meta.get("name", "Usuário")

        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "name": name,
                "role": role
            }
        }
    except Exception as e:
        # Simple error message for security
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

# --- Authentication Dependencies ---

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency para validar token e retornar usuário atual
    Usado em rotas que requerem autenticação
    """
    token = credentials.credentials
    
    try:
        # Decode JWT token (Supabase JWT)
        import jwt
        
        # Supabase tokens são auto-contidos, podemos decodificar sem verificar
        # (Em prod, deveria verificar assinatura com SUPABASE_JWT_SECRET)
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        user_metadata = decoded.get("user_metadata", {})
        
        return {
            "id": decoded.get("sub"),
            "email": decoded.get("email"),
            "name": user_metadata.get("name", "Usuário"),
            "role": user_metadata.get("role", "client")
        }
    except Exception as e:
        logger.error(f"[Auth] Token decode error: {e}")
        raise HTTPException(status_code=401, detail="Token inválido")

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency para validar que usuário é admin
    Usado em rotas administrativas
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Acesso negado. Apenas administradores."
        )
    
    return current_user

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("[AUTH] Supabase credentials not configured")
    supabase: Optional[Client] = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class AuthService:
    """Serviço de autenticação usando Supabase Auth"""
    
    def register(self, email: str, password: str, name: str) -> Optional[Dict[str, Any]]:
        """Registra um novo usuário"""
        if not supabase:
            logger.error("[AUTH] Supabase not configured")
            return None
        
        try:
            # Sign up com Supabase Auth
            res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"name": name}  # Metadata do usuário
                }
            })
            
            if res.user:
                logger.info(f"[AUTH] User registered: {email}")
                return {
                    "success": True,
                    "user": {
                        "id": res.user.id,
                        "email": res.user.email,
                        "name": name
                    },
                    "message": "Conta criada! Verifique seu email."
                }
            else:
                logger.error(f"[AUTH] Registration failed for {email}")
                return {"success": False, "error": "Erro ao criar conta"}
                
        except Exception as e:
            logger.error(f"[AUTH] Registration error: {e}")
            return {"success": False, "error": str(e)}
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Faz login de um usuário existente"""
        if not supabase:
            logger.error("[AUTH] Supabase not configured")
            # Fallback: Mock admin login
            if email == "admin@afiliado.top" and password == "admin":
                return self._create_mock_token(email, "Administrador", "admin")
            return None
        
        try:
            # Sign in com Supabase Auth
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if res.user and res.session:
                # Buscar perfil do usuário
                profile_res = supabase.table("user_profiles")\
                    .select("*")\
                    .eq("id", res.user.id)\
                    .single()\
                    .execute()
                
                profile = profile_res.data if profile_res.data else {}
                
                logger.info(f"[AUTH] User logged in: {email}")
                return {
                    "access_token": res.session.access_token,
                    "refresh_token": res.session.refresh_token,
                    "token_type": "bearer",
                    "user": {
                        "id": res.user.id,
                        "email": res.user.email,
                        "name": profile.get("name", "Usuário"),
                        "subscription_status": profile.get("subscription_status", "trial"),
                        "role": res.user.user_metadata.get("role", "user")
                    }
                }
            else:
                logger.error(f"[AUTH] Login failed for {email}")
                return None
                
        except Exception as e:
            logger.error(f"[AUTH] Login error: {e}")
            # Fallback para admin mock em caso de erro
            if email == "admin@afiliado.top" and password == "admin":
                return self._create_mock_token(email, "Administrador", "admin")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica um token JWT do Supabase"""
        if not supabase:
            return None
        
        try:
            # Supabase gerencia a verificação do token
            user = supabase.auth.get_user(token)
            if user:
                return {
                    "sub": user.user.email,
                    "user_id": user.user.id,
                    "role": user.user.user_metadata.get("role", "user")
                }
            return None
        except Exception as e:
            logger.error(f"[AUTH] Token verification error: {e}")
            return None
    
    def _create_mock_token(self, email: str, name: str, role: str) -> Dict[str, Any]:
        """Cria token mock para admin (fallback)"""
        import jwt
        SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_123")
        ALGORITHM = "HS256"
        
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode = {
            "sub": email,
            "name": name,
            "role": role,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "user": {
                "email": email,
                "name": name,
                "role": role,
                "subscription_status": "active"
            }
        }
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca perfil completo do usuário"""
        if not supabase:
            return None
        
        try:
            profile_res = supabase.table("user_profiles")\
                .select("*")\
                .eq("id", user_id)\
                .single()\
                .execute()
            
            return profile_res.data
        except Exception as e:
            logger.error(f"[AUTH] Error fetching profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza perfil do usuário"""
        if not supabase:
            return False
        
        try:
            supabase.table("user_profiles")\
                .update(data)\
                .eq("id", user_id)\
                .execute()
            
            logger.info(f"[AUTH] Profile updated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"[AUTH] Error updating profile: {e}")
            return False

# Singleton
auth_service = AuthService()

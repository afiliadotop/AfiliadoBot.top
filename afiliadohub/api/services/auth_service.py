import logging
from typing import Optional, Dict, Any
from ..utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)


class AuthService:
    """Serviço de autenticação usando Supabase Auth via SupabaseManager singleton."""

    def register(self, email: str, password: str, name: str) -> Optional[Dict[str, Any]]:
        """Registra um novo usuário."""
        supabase = get_supabase_manager()

        try:
            res = supabase.client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"name": name}},
                }
            )

            if res.user:
                logger.info(f"[AUTH] Usuário registrado: {email}")
                return {
                    "success": True,
                    "user": {"id": res.user.id, "email": res.user.email, "name": name},
                    "message": "Conta criada! Verifique seu email.",
                }

            logger.error(f"[AUTH] Falha no registro para {email}")
            return {"success": False, "error": "Erro ao criar conta"}

        except Exception as e:
            logger.error(f"[AUTH] Erro de registro: {e}")
            return {"success": False, "error": "Erro interno ao criar conta"}

    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Faz login de um usuário existente."""
        supabase = get_supabase_manager()

        try:
            res = supabase.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if res.user and res.session:
                user_meta = res.user.user_metadata or {}
                app_meta = res.user.app_metadata or {}
                role = app_meta.get("role") or user_meta.get("role", "client")

                logger.info(f"[AUTH] Login: {email} (role={role})")
                return {
                    "access_token": res.session.access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": res.user.id,
                        "email": res.user.email,
                        "name": user_meta.get("name", "Usuário"),
                        "role": role,
                    },
                }

            logger.error(f"[AUTH] Falha no login para {email}")
            return None

        except Exception as e:
            logger.error(f"[AUTH] Erro de login: {e}")
            return None

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica um token JWT via Supabase."""
        supabase = get_supabase_manager()

        try:
            user = supabase.client.auth.get_user(token)
            if user and user.user:
                user_meta = user.user.user_metadata or {}
                app_meta = user.user.app_metadata or {}
                role = app_meta.get("role") or user_meta.get("role", "client")
                return {
                    "sub": user.user.id,
                    "email": user.user.email,
                    "role": role,
                }
            return None
        except Exception as e:
            logger.error(f"[AUTH] Erro ao verificar token: {e}")
            return None

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca perfil completo do usuário."""
        supabase = get_supabase_manager()

        try:
            result = (
                supabase.client.table("user_profiles")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"[AUTH] Erro ao buscar perfil: {e}")
            return None

    def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza perfil do usuário."""
        supabase = get_supabase_manager()

        try:
            supabase.client.table("user_profiles").update(data).eq("id", user_id).execute()
            logger.info(f"[AUTH] Perfil atualizado para {user_id}")
            return True
        except Exception as e:
            logger.error(f"[AUTH] Erro ao atualizar perfil: {e}")
            return False


# Singleton
auth_service = AuthService()

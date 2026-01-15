"""
Telegram Settings Manager - Singleton Pattern
Gerencia configurações do Telegram com cache e refresh automático
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class TelegramSettingsManager:
    """
    Singleton para gerenciar configurações do Telegram
    - Cache com TTL de 5 minutos
    - Refresh automático quando expira
    - Método para forçar refresh
    """
    
    _instance: Optional['TelegramSettingsManager'] = None
    _settings: Optional[Dict] = None
    _last_refresh: Optional[datetime] = None
    _ttl_minutes = 5
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_settings(self, force_refresh: bool = False) -> Dict:
        """
        Retorna configurações atuais (com cache)
        
        Args:
            force_refresh: Se True, força atualização do cache
            
        Returns:
            Dict com bot_token, group_chat_id, etc.
        """
        now = datetime.utcnow()
        
        # Refresh se forçado ou cache expirou
        should_refresh = (
            force_refresh or 
            not self._settings or 
            not self._last_refresh or
            (now - self._last_refresh) > timedelta(minutes=self._ttl_minutes)
        )
        
        if should_refresh:
            self._refresh_from_db()
        
        return self._settings or {}
    
    def _refresh_from_db(self):
        """Atualiza cache do banco de dados"""
        try:
            from .supabase_client import get_supabase_manager
            
            supabase = get_supabase_manager()
            
            # Buscar configuração ativa mais recente
            result = supabase.client.table("telegram_settings")\
                .select("*")\
                .eq("is_active", True)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                self._settings = result.data[0]
                self._last_refresh = datetime.utcnow()
                logger.info("[Telegram Settings] Cache atualizado do banco")
            else:
                logger.warning("[Telegram Settings] Nenhuma configuração ativa encontrada")
                self._settings = {
                    "bot_token": "",
                    "group_chat_id": "",
                    "is_active": False
                }
                
        except Exception as e:
            logger.error(f"[Telegram Settings] Erro ao carregar do banco: {e}", exc_info=True)
            # Manter cache anterior se erro
            if not self._settings:
                self._settings = {
                    "bot_token": "",
                    "group_chat_id": "",
                    "is_active": False
                }
    
    def update_settings(
        self, 
        bot_token: str, 
        group_chat_id: str, 
        user_id: int,
        test_status: Optional[str] = None,
        test_bot_username: Optional[str] = None
    ) -> bool:
        """
        Atualiza configurações no banco e refresh cache
        
        Args:
            bot_token: Token do bot do Telegram
            group_chat_id: ID do grupo/canal
            user_id: ID do usuário que está atualizando
            test_status: Status do último teste (opcional)
            test_bot_username: Username do bot testado (opcional)
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            from .supabase_client import get_supabase_manager
            
            supabase = get_supabase_manager()
            
            # Desativar configurações antigas
            supabase.client.table("telegram_settings")\
                .update({"is_active": False})\
                .eq("is_active", True)\
                .execute()
            
            # Preparar dados
            data = {
                "bot_token": bot_token,
                "group_chat_id": group_chat_id,
                "is_active": True,
                "updated_by": user_id,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if test_status:
                data["test_status"] = test_status
                data["last_tested_at"] = datetime.utcnow().isoformat()
            
            if test_bot_username:
                data["test_bot_username"] = test_bot_username
            
            # Inserir nova configuração
            result = supabase.client.table("telegram_settings")\
                .insert(data)\
                .execute()
            
            # Refresh cache imediatamente
            self._refresh_from_db()
            
            logger.info(f"[Telegram Settings] Configurações atualizadas por user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"[Telegram Settings] Erro ao atualizar: {e}", exc_info=True)
            return False
    
    def get_bot_token(self) -> Optional[str]:
        """Retorna bot token atual"""
        settings = self.get_settings()
        token = settings.get("bot_token", "")
        if token:
            return token

        # Fallback .env for backward compatibility
        import os
        return os.getenv("TELEGRAM_BOT_TOKEN")
    
    def get_group_chat_id(self) -> Optional[str]:
        """Retorna group chat ID atual"""
        settings = self.get_settings()
        chat_id = settings.get("group_chat_id", "")
        if chat_id:
            return chat_id

        # Fallback .env
        import os
        return os.getenv("TELEGRAM_CHANNEL_ID")
    
    def is_configured(self) -> bool:
        """Verifica se está configurado"""
        settings = self.get_settings()
        
        # Check DB first
        if (settings.get("is_active") and 
            settings.get("bot_token") and 
            settings.get("group_chat_id")):
            return True
            
        # Check env var fallback
        import os
        return bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHANNEL_ID"))
    
    def get_cache_age_seconds(self) -> Optional[int]:
        """Retorna idade do cache em segundos"""
        if not self._last_refresh:
            return None
        
        age = datetime.utcnow() - self._last_refresh
        return int(age.total_seconds())


# Instância global singleton
telegram_settings = TelegramSettingsManager()

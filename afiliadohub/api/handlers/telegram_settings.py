"""
Telegram Settings API Endpoints
Admin-only routes for managing Telegram bot configuration
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Optional
import logging
from telegram import Bot

from .auth import get_current_admin
from ..utils.telegram_settings_manager import telegram_settings

router = APIRouter(prefix="/telegram/settings", tags=["telegram-settings"])
logger = logging.getLogger(__name__)


# ==================== MODELS ====================

class UpdateSettingsRequest(BaseModel):
    bot_token: str = Field(..., description="Token do bot do Telegram")
    group_chat_id: str = Field(..., description="ID do grupo/canal (-100...)")

class TestConnectionRequest(BaseModel):
    bot_token: str = Field(..., description="Token do bot para testar")
    group_chat_id: str = Field(..., description="ID do grupo para testar")


# ==================== ENDPOINTS ====================

@router.get("")
async def get_telegram_settings(
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Get current Telegram settings
    
    Returns masked bot token for security
    Admin only
    """
    try:
        settings = telegram_settings.get_settings()
        
        # Mascarar token para segurança
        if settings.get("bot_token"):
            token = settings["bot_token"]
            if len(token) > 20:
                settings["bot_token_masked"] = f"{token[:10]}...{token[-10:]}"
            else:
                settings["bot_token_masked"] = "***"
            
            # Remover token completo da resposta
            del settings["bot_token"]
        
        # Adicionar info de cache
        cache_age = telegram_settings.get_cache_age_seconds()
        
        return {
            "success": True,
            "settings": settings,
            "cache_age_seconds": cache_age,
            "is_configured": telegram_settings.is_configured()
        }
        
    except Exception as e:
        logger.error(f"[Telegram Settings API] Erro ao buscar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
async def update_telegram_settings(
    request: UpdateSettingsRequest,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Update Telegram settings
    
    Validates input and saves to database
    Admin only
    """
    try:
        # Validar inputs
        if not request.bot_token or not request.group_chat_id:
            raise HTTPException(
                status_code=400,
                detail="Bot token e group chat ID são obrigatórios"
            )
        
        # Validar formato do token (formato Telegram: números:AAF/AAE...)
        if ":" not in request.bot_token:
            raise HTTPException(
                status_code=400,
                detail="Token do bot inválido. Formato esperado: 1234567890:AAF..."
            )
        
        # Validar formato do chat ID (grupos começam com -)
        if not request.group_chat_id.startswith("-"):
            raise HTTPException(
                status_code=400,
                detail="Group chat ID deve começar com '-' (ex: -1001234567890)"
            )
        
        # Atualizar no banco
        success = telegram_settings.update_settings(
            bot_token=request.bot_token,
            group_chat_id=request.group_chat_id,
            user_id=current_admin["id"]
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar configurações no banco de dados"
            )
        
        logger.info(f"[Telegram Settings API] Configurações atualizadas por admin:{current_admin['id']}")
        
        return {
            "success": True,
            "message": "Configurações atualizadas com sucesso!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Telegram Settings API] Erro ao atualizar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_telegram_connection(
    request: TestConnectionRequest,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Test Telegram bot connection
    
    Sends a test message to verify credentials
    Admin only
    """
    try:
        # Criar bot com token fornecido
        bot = Bot(token=request.bot_token)
        
        # Buscar informações do bot
        bot_info = await bot.get_me()
        
        logger.info(f"[Telegram Test] Bot conectado: @{bot_info.username}")
        
        # Tentar enviar mensagem de teste (texto simples, sem Markdown)
        from datetime import datetime
        test_message = (
            f"✅ Teste de Conexão\n\n"
            f"Bot: @{bot_info.username}\n"
            f"Admin: {current_admin.get('username', 'N/A')}\n"
            f"Data: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        sent_message = await bot.send_message(
            chat_id=request.group_chat_id,
            text=test_message
        )
        
        logger.info(f"[Telegram Test] Mensagem enviada com sucesso! Message ID: {sent_message.message_id}")
        
        return {
            "success": True,
            "bot_username": bot_info.username,
            "bot_name": bot_info.first_name,
            "bot_id": bot_info.id,
            "message": f"Conexão testada com sucesso! Mensagem enviada ao grupo.",
            "message_id": sent_message.message_id
        }
        
    except Exception as e:
        logger.error(f"[Telegram Test] Erro ao testar: {e}", exc_info=True)
        
        # Mensagens de erro mais amigáveis
        error_msg = str(e)
        
        if "Unauthorized" in error_msg:
            error_detail = "Token do bot inválido ou revogado"
        elif "Chat not found" in error_msg:
            error_detail = "Group Chat ID não encontrado. Verifique se o bot está no grupo."
        elif "bot was blocked" in error_msg:
            error_detail = "Bot foi bloqueado no grupo"
        else:
            error_detail = f"Erro ao testar conexão: {error_msg}"
        
        raise HTTPException(status_code=400, detail=error_detail)


@router.post("/refresh")
async def refresh_telegram_cache(
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Force refresh settings cache
    
    Useful after manual database updates
    Admin only
    """
    try:
        telegram_settings.get_settings(force_refresh=True)
        
        logger.info(f"[Telegram Settings API] Cache atualizado manualmente por admin:{current_admin['id']}")
        
        return {
            "success": True,
            "message": "Cache de configurações atualizado!",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[Telegram Settings API] Erro ao refresh: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_telegram_status(
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Get Telegram integration status
    
    Returns configuration and connectivity info
    Admin only
    """
    try:
        is_configured = telegram_settings.is_configured()
        settings = telegram_settings.get_settings()
        
        status = {
            "is_configured": is_configured,
            "is_active": settings.get("is_active", False),
            "has_bot_token": bool(settings.get("bot_token")),
            "has_group_chat_id": bool(settings.get("group_chat_id")),
            "last_tested": settings.get("last_tested_at"),
            "test_status": settings.get("test_status"),
            "test_bot_username": settings.get("test_bot_username"),
            "cache_age_seconds": telegram_settings.get_cache_age_seconds()
        }
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"[Telegram Settings API] Erro ao buscar status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Import datetime
from datetime import datetime

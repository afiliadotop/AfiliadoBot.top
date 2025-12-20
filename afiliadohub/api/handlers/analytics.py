"""
Handler para analytics - Refatorado para uso de Service
"""
import logging
from typing import Dict, Any
from datetime import datetime
from ..services.db_service import db_service

logger = logging.getLogger(__name__)

async def get_system_statistics() -> Dict[str, Any]:
    """Retorna estatísticas gerais do sistema via DatabaseService"""
    try:
        return await db_service.get_dashboard_stats()
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return {"error": str(e)}

async def get_daily_statistics(date: datetime.date = None) -> Dict[str, Any]:
    """Retorna estatísticas do dia"""
    # TODO: Implement in Service
    return {
        "date": datetime.now().isoformat(),
        "products_added": 0,
        "telegram_sends": 0
    }

async def get_product_analytics(product_id: int) -> Dict[str, Any]:
    """Retorna analytics de um produto específico"""
    return {}
